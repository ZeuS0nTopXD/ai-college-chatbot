from backend.database.database import SessionLocal
from backend.models.faculty import Faculty
from backend.models.office import Office
from backend.models.result import Result
from backend.models.timetable import Timetable
from backend.models.knowledge import KnowledgeBase
from backend.models.academic import AcademicEvent
from backend.scripts.seed_official_vsit import sync_official_vsit, ensure_official_records


def test_official_sync_loads_published_records_and_clears_samples(client):
    sync_official_vsit()

    db = SessionLocal()
    try:
        assert db.query(Faculty).filter(Faculty.name == "Dr. Asif Rampurawala").count() == 1
        assert db.query(Faculty).count() >= 70
        assert db.query(Office).filter(Office.contact_email == "principal@vsit.edu.in").count() == 1
        assert db.query(Timetable).count() >= 100
        assert db.query(Result).count() == 0
        topics = {row.topic for row in db.query(KnowledgeBase).all()}
        assert "Admissions" in topics
        assert "Placements" in topics
        assert "Library" in topics
    finally:
        db.close()


def test_official_record_refresh_adds_new_records_without_clearing_existing(client):
    ensure_official_records()
    db = SessionLocal()
    try:
        assert db.query(KnowledgeBase).filter(KnowledgeBase.topic == "Admissions").count() >= 1
        assert db.query(Office).filter(Office.office_name == "Library").count() == 1
    finally:
        db.close()


def test_signed_winter_2026_notice_seeds_date_only_academic_events_once(client):
    from backend.data.official_academic_events import OFFICIAL_ACADEMIC_EVENTS, SOURCE_URL

    assert len(OFFICIAL_ACADEMIC_EVENTS) == 24
    ensure_official_records()
    ensure_official_records()

    db = SessionLocal()
    try:
        rows = db.query(AcademicEvent).filter(AcademicEvent.resource_url == SOURCE_URL).all()
        assert len(rows) == 24
        assert all(row.starts_at.strftime("%Y-%m-%d %H:%M") == "2026-10-12 00:00" for row in rows)
    finally:
        db.close()

    response = client.get("/api/academics", params={"course": "BSc IT", "semester": "5"})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["resource_url"] == SOURCE_URL


def test_official_timetable_pdf_dataset_covers_tyit_divisions():
    from backend.data.official_timetable_data import OFFICIAL_TIMETABLE_DATA

    assert OFFICIAL_TIMETABLE_DATA
    assert {row["division"] for row in OFFICIAL_TIMETABLE_DATA} == {"A", "B", "C", "D", "E"}
    assert {row["academic_year"] for row in OFFICIAL_TIMETABLE_DATA} == {"2026-27"}
    assert {row["semester"] for row in OFFICIAL_TIMETABLE_DATA} == {"Odd Semester"}
    assert {row["effective_from"] for row in OFFICIAL_TIMETABLE_DATA} == {"2026-07-13"}
    assert sum(row["session_type"] == "Practical" for row in OFFICIAL_TIMETABLE_DATA) >= 20
    assert all(row["session_type"] == "Practical" for row in OFFICIAL_TIMETABLE_DATA if "X103" in row["room"].replace("-", ""))
