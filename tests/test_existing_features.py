from datetime import time

from backend.database.database import SessionLocal
from backend.models.knowledge import KnowledgeBase
from backend.models.office import Office
from backend.models.result import Result
from backend.models.timetable import Timetable
from backend.models.faculty import Faculty
import pytest


def seed(record):
    db = SessionLocal()
    try:
        db.add(record)
        db.commit()
    finally:
        db.close()


def seed_timetable():
    seed(
        Timetable(
            academic_year="2026-27",
            semester="Odd Semester",
            course="B.Sc. Information Technology",
            division="A",
            day="Monday",
            start_time=time(9, 0),
            end_time=time(10, 0),
            subject_code="IOT",
            subject_name="Internet of Things",
            teacher_names="Prof. Asha Patil",
            room="Lab 2",
            session_type="Practical",
        )
    )


def test_timetable_endpoint_uses_current_model_fields(client):
    seed_timetable()

    response = client.get("/timetable/B.Sc.%20Information%20Technology/A/Monday")

    assert response.status_code == 200
    item = response.json()["timetable"][0]
    assert item == {
        "start_time": "09:00:00",
        "end_time": "10:00:00",
        "subject": "Internet of Things",
        "teacher": "Prof. Asha Patil",
        "room": "Lab 2",
        "lecture_type": "Practical",
    }


def test_timetable_seed_script_does_not_insert_unverified_rows(client):
    import backend.scripts.seed_timetable as seed_script

    seed_script.seed_timetable()

    db = SessionLocal()
    try:
        assert db.query(Timetable).count() == 0
    finally:
        db.close()


def test_chat_answers_teacher_from_timetable(client):
    seed_timetable()

    response = client.post("/chat", json={"message": "Who teaches IOT?"})

    assert response.status_code == 200
    assert response.json()["category"] == "FACULTY"
    assert "Prof. Asha Patil" in response.json()["bot_response"]


def test_chat_answers_short_head_of_department_variant(client):
    seed(
        Faculty(
            name="Dr. Asif Rampurawala",
            department="Computing",
            designation="Vice Principal and Head, Department of Computing",
            email="asif.rampurawala@vsit.edu.in",
            is_hod=True,
        )
    )

    response = client.post(
        "/chat",
        json={"message": "who is the head of computing"},
    )

    assert response.status_code == 200
    assert response.json()["category"] == "FACULTY"
    assert "Dr. Asif Rampurawala" in response.json()["bot_response"]


def test_chat_answers_typo_tolerant_head_question(client):
    seed(
        Faculty(
            name="Dr. Asif Rampurawala",
            department="Computing",
            designation="Vice Principal and Head, Department of Computing",
            email="asif.rampurawala@vsit.edu.in",
            is_hod=True,
        )
    )

    response = client.post("/chat", json={"message": "wht is the hod of computng"})

    assert response.status_code == 200
    assert "Dr. Asif Rampurawala" in response.json()["bot_response"]


@pytest.mark.parametrize(
    "question",
    [
        "who runs computing",
        "who is in charge of the computing department",
        "tell me who leads computing",
    ],
)
def test_chat_understands_natural_head_of_department_phrasing(client, question):
    seed(
        Faculty(
            name="Dr. Asif Rampurawala",
            department="Computing",
            designation="Vice Principal and Head, Department of Computing",
            email="asif.rampurawala@vsit.edu.in",
            is_hod=True,
        )
    )

    response = client.post("/chat", json={"message": question})

    assert response.status_code == 200
    assert response.json()["category"] == "FACULTY"
    assert "Dr. Asif Rampurawala" in response.json()["bot_response"]


def test_chat_answers_office_location(client):
    seed(
        Office(
            office_name="Student Section",
            purpose="Student documents",
            timings="10 AM to 4 PM",
            location="Ground Floor",
            is_active=True,
        )
    )

    response = client.post(
        "/chat",
        json={"message": "Where is the student section?"},
    )

    assert response.status_code == 200
    assert response.json()["category"] == "OFFICE"
    assert "Ground Floor" in response.json()["bot_response"]


def test_chat_returns_result_link(client):
    seed(
        Result(
            course="TYIT",
            semester="4",
            batch="2025-26",
            year="2026",
            title="BSc IT Semester 4 Result",
            url="https://vsit.edu.in/result/bsc-it-sem-4",
        )
    )

    response = client.post(
        "/chat",
        json={"message": "Show BSc IT semester 4 result"},
    )

    assert response.status_code == 200
    assert response.json()["category"] == "RESULT"
    assert response.json()["result_url"] == "https://vsit.edu.in/result/bsc-it-sem-4"


def test_chat_returns_matching_knowledge(client):
    seed(
        KnowledgeBase(
            category="VSIT",
            topic="attendance",
            question="What is the attendance requirement at VSIT?",
            answer="Students should follow the current official attendance policy.",
        )
    )

    response = client.post(
        "/chat",
        json={"message": "What is the attendance requirement at VSIT?"},
    )

    assert response.status_code == 200
    assert response.json()["category"] == "VSIT"
    assert response.json()["bot_response"] == (
        "Students should follow the current official attendance policy."
    )


def test_chat_searches_admin_knowledge_entries_even_when_classifier_is_general(client):
    seed(
        KnowledgeBase(
            category="VSIT",
            topic="student support",
            question="How do I get a student ID card?",
            answer="Visit the student section with your admission receipt.",
        )
    )

    response = client.post("/chat", json={"message": "How do I get a student ID card?"})

    assert response.status_code == 200
    assert response.json()["bot_response"] == (
        "Visit the student section with your admission receipt."
    )


def test_general_ai_path_receives_ranked_knowledge_context(client, monkeypatch):
    seed(
        KnowledgeBase(
            category="GENERAL",
            topic="student support",
            question="Can students reserve the innovation lab?",
            answer="Students can reserve it through the Computing department office.",
        )
    )
    from backend.routes.chat import _knowledge_context

    db = SessionLocal()
    try:
        context = _knowledge_context(db, "Can I book the innovation lab?")
    finally:
        db.close()

    assert "Computing department office" in context


def test_exact_admin_entry_wins_before_specialist_router(client):
    seed(
        KnowledgeBase(
            category="GENERAL",
            topic="student support",
            question="What is the timetable policy?",
            answer="The timetable policy is published by the Computing department.",
        )
    )

    response = client.post("/chat", json={"message": "What is the timetable policy?"})

    assert response.status_code == 200
    assert response.json()["bot_response"] == (
        "The timetable policy is published by the Computing department."
    )


def test_profile_division_does_not_turn_department_question_into_timetable(client):
    response = client.post(
        "/chat",
        json={
            "message": "I need help finding the computing department",
            "course": "B.Sc. Information Technology",
            "division": "A",
        },
    )

    assert response.status_code == 200
    assert response.json()["category"] != "TIMETABLE"


def test_chat_answers_official_admission_and_library_questions(client):
    from backend.scripts.seed_knowledge import seed_knowledge

    seed_knowledge()
    admission = client.post("/chat", json={"message": "how do I apply for admission"})
    library = client.post("/chat", json={"message": "what are the library timings"})

    assert "admission" in admission.json()["bot_response"].lower()
    assert "8:00 am" in library.json()["bot_response"].lower()


def test_chat_answers_official_student_support_and_course_questions(client):
    from backend.scripts.seed_knowledge import seed_knowledge

    seed_knowledge()
    grievance = client.post("/chat", json={"message": "How do I file a student grievance?"})
    courses = client.post("/chat", json={"message": "Which courses are offered at VSIT?"})

    assert "grievance" in grievance.json()["bot_response"].lower()
    assert "b.sc. information technology" in courses.json()["bot_response"].lower()


def test_chat_works_when_ollama_is_unavailable(client, monkeypatch):
    import backend.services.ai_service as ai_service

    def unavailable(*args, **kwargs):
        raise ai_service.requests.RequestException("offline")

    monkeypatch.setattr(ai_service.requests, "post", unavailable)

    response = client.post(
        "/chat",
        json={"message": "Give me a general study tip"},
    )

    assert response.status_code == 200
    assert response.json()["bot_response"]
    assert "unavailable" in response.json()["bot_response"].lower()
    assert "local ai service is not running" not in response.json()["bot_response"].lower()


def test_chat_answers_greeting_without_ai_fallback(client):
    response = client.post("/chat", json={"message": "hello"})

    assert response.status_code == 200
    assert response.json()["category"] == "GREETING"
    assert "help" in response.json()["bot_response"].lower()
    assert "verified answer" not in response.json()["bot_response"].lower()


@pytest.mark.parametrize("message", ["how are you", "what's up assistant"])
def test_chat_handles_small_talk_as_greeting(client, message):
    response = client.post("/chat", json={"message": message})
    assert response.status_code == 200
    assert response.json()["category"] == "GREETING"


@pytest.mark.parametrize("message", ["thanks", "thank you", "bye", "help"])
def test_chat_handles_short_conversation_messages(client, message):
    response = client.post("/chat", json={"message": message})
    assert response.status_code == 200
    assert response.json()["category"] == "GREETING"


def test_placement_date_question_does_not_return_office_directory(client):
    response = client.post("/chat", json={"message": "when is placement drive"})
    assert response.status_code == 200
    assert "placement cell" not in response.json()["bot_response"].lower()


@pytest.mark.parametrize("message", ["how are you", "how do placements work"])
def test_broad_office_detector_does_not_hijack_conversation_or_placement_knowledge(client, message):
    response = client.post("/chat", json={"message": message})
    assert response.status_code == 200
    assert response.json()["category"] != "OFFICE"


@pytest.mark.parametrize("message", ["I feel stressed about exams", "I am overwhelmed and anxious"])
def test_chat_supports_student_wellbeing_questions(client, message):
    response = client.post("/chat", json={"message": message})
    assert response.status_code == 200
    assert response.json()["category"] == "WELLBEING"
    assert "support" in response.json()["bot_response"].lower()


def test_chat_escalates_immediate_safety_concern(client):
    response = client.post("/chat", json={"message": "I might hurt myself"})
    assert response.status_code == 200
    assert response.json()["category"] == "WELLBEING_CRISIS"
    assert "emergency" in response.json()["bot_response"].lower()


def test_verified_vsit_question_wins_over_timetable_detector(client, monkeypatch):
    response = client.post("/chat", json={"message": "what is VSIT?"})

    assert response.status_code == 200
    assert response.json()["category"] == "VSIT"
    assert "specify the day for the timetable" not in response.json()["bot_response"].lower()


def test_greeting_wins_over_timetable_detector(client, monkeypatch):
    import backend.routes.chat as chat_route

    monkeypatch.setattr(chat_route, "is_timetable_question", lambda _message: True)

    response = client.post("/chat", json={"message": "hi"})

    assert response.status_code == 200
    assert response.json()["category"] == "GREETING"
    assert "specify the day for the timetable" not in response.json()["bot_response"].lower()


@pytest.mark.parametrize("message", ["hi there", "hey bot", "good morning assistant"])
def test_chat_understands_natural_greetings(client, message):
    response = client.post("/chat", json={"message": message})

    assert response.status_code == 200
    assert response.json()["category"] == "GREETING"
    assert "help" in response.json()["bot_response"].lower()
    assert "unavailable" not in response.json()["bot_response"].lower()


def test_chat_explains_private_data_boundary(client):
    response = client.post("/chat", json={"message": "What are my attendance marks?"})

    assert response.status_code == 200
    assert response.json()["category"] == "PRIVATE_DATA"
    assert "private student records" in response.json()["bot_response"].lower()
