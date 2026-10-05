"""Refresh local data with facts published by VSIT and its official records."""

from backend.data.official_vsit_data import (
    OFFICIAL_FACULTY_DATA,
    OFFICIAL_HISTORICAL_FACULTY_DATA,
    OFFICIAL_KNOWLEDGE_DATA,
    OFFICIAL_OFFICE_DATA,
)
from backend.data.official_academic_events import OFFICIAL_ACADEMIC_EVENTS
from backend.models.academic import AcademicEvent
from backend.models.knowledge import KnowledgeBase
from backend.database.database import SessionLocal
from backend.models.faculty import Faculty
from backend.models.office import Office
from backend.models.result import Result
from backend.models.timetable import Timetable
from datetime import date, datetime, time
from backend.data.official_timetable_data import OFFICIAL_TIMETABLE_DATA


def _parse_time(value: str | time) -> time:
    if isinstance(value, time):
        return value
    for pattern in ("%I:%M %p", "%H:%M"):
        try:
            return datetime.strptime(value.strip(), pattern).time()
        except ValueError:
            continue
    raise ValueError(f"Unsupported timetable time: {value}")


def _timetable_values(item):
    return {
        **item,
        "effective_from": date.fromisoformat(item["effective_from"]),
        "start_time": _parse_time(item["start_time"]),
        "end_time": _parse_time(item["end_time"]),
    }
from backend.scripts.seed_knowledge import seed_knowledge


def ensure_official_records():
    """Add newly published records without overwriting admin-managed data."""
    db = SessionLocal()
    try:
        existing_questions = {row.question for row in db.query(KnowledgeBase).all()}
        existing_faculty = {row.name for row in db.query(Faculty).all()}
        existing_offices = {row.office_name for row in db.query(Office).all()}
        existing_events = {
            (row.title, row.course, row.semester, row.starts_at)
            for row in db.query(AcademicEvent).all()
        }
        existing_timetable = {
            (row.academic_year, row.semester, row.course, row.division, row.day,
             row.start_time, row.end_time, row.subject_code, row.room)
            for row in db.query(Timetable).all()
        }
        db.add_all(
            KnowledgeBase(**item)
            for item in OFFICIAL_KNOWLEDGE_DATA
            if item["question"] not in existing_questions
        )
        db.add_all(
            Faculty(**item)
            for item in [*OFFICIAL_FACULTY_DATA, *OFFICIAL_HISTORICAL_FACULTY_DATA]
            if item["name"] not in existing_faculty
        )
        db.add_all(
            Office(**item)
            for item in OFFICIAL_OFFICE_DATA
            if item["office_name"] not in existing_offices
        )
        db.add_all(
            AcademicEvent(**item)
            for item in OFFICIAL_ACADEMIC_EVENTS
            if (item["title"], item["course"], item["semester"], item["starts_at"])
            not in existing_events
        )
        for item in OFFICIAL_TIMETABLE_DATA:
            values = _timetable_values(item)
            key = (values["academic_year"], values["semester"], values["course"], values["division"],
                   values["day"], values["start_time"], values["end_time"],
                   item["subject_code"], item["room"])
            if key not in existing_timetable:
                db.add(Timetable(**values))
            else:
                existing = db.query(Timetable).filter(
                    Timetable.academic_year == values["academic_year"],
                    Timetable.semester == values["semester"],
                    Timetable.course == values["course"],
                    Timetable.division == values["division"],
                    Timetable.day == values["day"],
                    Timetable.start_time == values["start_time"],
                    Timetable.end_time == values["end_time"],
                    Timetable.subject_code == values["subject_code"],
                    Timetable.room == values["room"],
                ).first()
                if existing and existing.session_type != values["session_type"]:
                    existing.session_type = values["session_type"]
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def sync_official_vsit():
    seed_knowledge()
    db = SessionLocal()
    try:
        existing_events = {
            (row.title, row.course, row.semester, row.starts_at)
            for row in db.query(AcademicEvent).all()
        }
        db.query(Faculty).delete(synchronize_session=False)
        db.query(Office).delete(synchronize_session=False)
        db.query(Timetable).delete(synchronize_session=False)
        db.query(Result).delete(synchronize_session=False)
        db.add_all(Faculty(**item) for item in [*OFFICIAL_FACULTY_DATA, *OFFICIAL_HISTORICAL_FACULTY_DATA])
        db.add_all(Office(**item) for item in OFFICIAL_OFFICE_DATA)
        db.add_all(Timetable(**_timetable_values(item))
                   for item in OFFICIAL_TIMETABLE_DATA)
        db.add_all(
            AcademicEvent(**item)
            for item in OFFICIAL_ACADEMIC_EVENTS
            if (item["title"], item["course"], item["semester"], item["starts_at"])
            not in existing_events
        )
        db.commit()
        print("Loaded verified faculty and office records.")
        print(f"Loaded {len(OFFICIAL_TIMETABLE_DATA)} official TYIT timetable periods.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    sync_official_vsit()
