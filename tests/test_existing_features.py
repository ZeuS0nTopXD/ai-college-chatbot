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
