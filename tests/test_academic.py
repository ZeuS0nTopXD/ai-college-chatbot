from datetime import datetime

from backend.database.database import SessionLocal
from backend.models.academic import AcademicEvent


def add_event(**overrides):
    values = {
        "title": "Semester 4 Examination",
        "description": "End-semester written examination",
        "event_type": "examination",
        "course": "BSc IT",
        "semester": "4",
        "starts_at": datetime(2027, 3, 10, 10, 0),
        "ends_at": datetime(2027, 3, 20, 13, 0),
        "location": "VSIT Examination Hall",
        "resource_url": "https://vsit.edu.in/exams/semester-4",
        "is_published": True,
    }
    values.update(overrides)
    db = SessionLocal()
    try:
        event = AcademicEvent(**values)
        db.add(event)
        db.commit()
        db.refresh(event)
        return event.id
    finally:
        db.close()


def test_public_academics_hide_drafts(client):
    add_event(title="Published Exam")
    add_event(title="Internal Draft", is_published=False)

    response = client.get("/api/academics")

    assert response.status_code == 200
    assert [event["title"] for event in response.json()] == ["Published Exam"]


def test_public_academics_filter_course_and_semester_case_insensitively(client):
    add_event(title="IT Semester 4", course="BSc IT", semester="4")
    add_event(title="CS Semester 4", course="BSc CS", semester="4")
    add_event(title="IT Semester 6", course="BSc IT", semester="6")

    response = client.get(
        "/api/academics",
        params={"course": "bsc it", "semester": "4"},
    )

    assert response.status_code == 200
    assert [event["title"] for event in response.json()] == ["IT Semester 4"]


def test_academic_question_returns_nearest_matching_event(client):
    add_event(title="Semester 4 Examination", starts_at=datetime(2027, 3, 10, 10))
    add_event(title="Semester 4 Examination Retest", starts_at=datetime(2027, 4, 10, 10))

    response = client.post(
        "/chat",
        json={"message": "When is the BSc IT semester 4 exam?"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "ACADEMIC"
    assert "10 March 2027" in body["bot_response"]
    assert body["event_id"]
    assert body["resource_url"] == "https://vsit.edu.in/exams/semester-4"


def test_academic_event_may_omit_course_and_semester(client):
    add_event(
        title="Foundation Day Holiday",
        event_type="holiday",
        course=None,
        semester=None,
    )

    response = client.get("/api/academics", params={"course": "BSc IT"})

    assert response.status_code == 200
    assert response.json()[0]["title"] == "Foundation Day Holiday"


def test_empty_or_oversized_chat_message_is_bounded(client):
    empty = client.post("/chat", json={"message": "   "})
    oversized = client.post("/chat", json={"message": "x" * 4001})

    assert empty.status_code == 200
    assert empty.json()["bot_response"] == "Please enter a question."
    assert oversized.status_code == 422
