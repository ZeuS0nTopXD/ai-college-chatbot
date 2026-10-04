"""Refresh local data with facts published on vsit.edu.in.

The public site does not publish a current timetable or individual student
results, so those tables are deliberately cleared rather than filled with
sample rows.
"""

from backend.data.official_vsit_data import OFFICIAL_FACULTY_DATA, OFFICIAL_OFFICE_DATA
from backend.database.database import SessionLocal
from backend.models.faculty import Faculty
from backend.models.office import Office
from backend.models.result import Result
from backend.models.timetable import Timetable
from backend.scripts.seed_knowledge import seed_knowledge


def sync_official_vsit():
    seed_knowledge()
    db = SessionLocal()
    try:
        db.query(Faculty).delete(synchronize_session=False)
        db.query(Office).delete(synchronize_session=False)
        db.query(Timetable).delete(synchronize_session=False)
        db.query(Result).delete(synchronize_session=False)
        db.add_all(Faculty(**item) for item in OFFICIAL_FACULTY_DATA)
        db.add_all(Office(**item) for item in OFFICIAL_OFFICE_DATA)
        db.commit()
        print("Loaded verified faculty and office records.")
        print("Cleared timetable and result sample records: no current public official data was found.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    sync_official_vsit()
