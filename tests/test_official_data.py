from backend.database.database import SessionLocal
from backend.models.faculty import Faculty
from backend.models.office import Office
from backend.models.result import Result
from backend.models.timetable import Timetable
from backend.scripts.seed_official_vsit import sync_official_vsit


def test_official_sync_loads_published_records_and_clears_samples(client):
    sync_official_vsit()

    db = SessionLocal()
    try:
        assert db.query(Faculty).filter(Faculty.name == "Dr. Asif Rampurawala").count() == 1
        assert db.query(Office).filter(Office.contact_email == "principal@vsit.edu.in").count() == 1
        assert db.query(Timetable).count() == 0
        assert db.query(Result).count() == 0
    finally:
        db.close()
