from datetime import datetime, timedelta

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
    oversized_input = "x" * 1_000_000
    oversized = client.post("/chat", json={"message": oversized_input})

    assert empty.status_code == 200
    assert empty.json()["bot_response"] == "Please enter a question."
    assert oversized.status_code == 422
    assert len(oversized.content) < 5_000
    assert oversized_input.encode() not in oversized.content


def test_academic_filter_includes_an_event_already_in_progress(client):
    add_event(
        title="Multi-day Examination",
        starts_at=datetime(2027, 3, 9, 9),
        ends_at=datetime(2027, 3, 11, 17),
    )

    response = client.get(
        "/api/academics",
        params={"from_date": "2027-03-10T12:00:00"},
    )

    assert response.status_code == 200
    assert [item["title"] for item in response.json()] == ["Multi-day Examination"]


def test_academic_chat_includes_an_event_already_in_progress(client):
    now = datetime.now()
    add_event(
        title="Ongoing Semester Examination",
        starts_at=now - timedelta(days=1),
        ends_at=now + timedelta(days=1),
    )

    response = client.post("/chat", json={"message": "When is the semester exam?"})

    assert response.status_code == 200
    assert response.json()["category"] == "ACADEMIC"
    assert "Ongoing Semester Examination" in response.json()["bot_response"]


def test_academic_question_does_not_return_wrong_course_or_semester(client):
    add_event(
        title="BSc CS Semester 6 Examination",
        course="BSc CS",
        semester="6",
    )

    response = client.post(
        "/chat",
        json={"message": "When is the BSc IT semester 4 exam?"},
    )

    assert response.status_code == 200
    assert response.json()["category"] == "ACADEMIC"
    assert "could not find" in response.json()["bot_response"].lower()
    assert "BSc CS" not in response.json()["bot_response"]


def test_structured_academic_event_beats_a_weak_document_match(client):
    from backend.models.document import Document, DocumentChunk

    add_event(title="Semester 4 Examination", starts_at=datetime(2027, 3, 10, 10))
    db = SessionLocal()
    try:
        document = Document(
            title="General Examination Instructions",
            category="examination",
            filename="instructions.txt",
            stored_filename="instructions.txt",
            page_count=1,
            status="ready",
        )
        db.add(document)
        db.flush()
        db.add(
            DocumentChunk(
                document_id=document.id,
                page_number=1,
                chunk_index=0,
                content="Students attending an examination should bring pencils.",
            )
        )
        db.commit()
    finally:
        db.close()

    response = client.post(
        "/chat",
        json={"message": "When is the BSc IT semester 4 examination?"},
    )

    assert response.json()["category"] == "ACADEMIC"
    assert "10 March 2027" in response.json()["bot_response"]


def test_missing_official_deadline_does_not_use_unrestricted_ai(client, monkeypatch):
    import backend.routes.chat as chat_route

    def fail_if_called(*args, **kwargs):
        raise AssertionError("Official deadline questions must not call the AI fallback")

    monkeypatch.setattr(chat_route, "get_ai_response", fail_if_called)

    response = client.post(
        "/chat",
        json={"message": "What is the application deadline?"},
    )

    assert response.status_code == 200
    assert response.json()["category"] == "ACADEMIC"
    assert "could not find" in response.json()["bot_response"].lower()
    assert "official" in response.json()["bot_response"].lower()
