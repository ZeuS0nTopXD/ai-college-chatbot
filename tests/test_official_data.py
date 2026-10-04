from backend.database.database import SessionLocal
from backend.models.faculty import Faculty
from backend.models.office import Office
from backend.models.result import Result
from backend.models.timetable import Timetable
from backend.models.knowledge import KnowledgeBase
from backend.scripts.seed_official_vsit import sync_official_vsit, ensure_official_records


def test_official_sync_loads_published_records_and_clears_samples(client):
    sync_official_vsit()

    db = SessionLocal()
    try:
        assert db.query(Faculty).filter(Faculty.name == "Dr. Asif Rampurawala").count() == 1
        assert db.query(Faculty).count() >= 70
        assert db.query(Office).filter(Office.contact_email == "principal@vsit.edu.in").count() == 1
        assert db.query(Timetable).count() == 0
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
