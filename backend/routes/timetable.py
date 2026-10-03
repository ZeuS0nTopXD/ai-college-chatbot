from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.database import SessionLocal
from backend.models.timetable import Timetable


router = APIRouter()


# Database connection
def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# Get timetable by course, division and day
@router.get("/timetable/{course}/{division}/{day}")
def get_timetable_by_day(
    course: str,
    division: str,
    day: str,
    db: Session = Depends(get_db)
):

    timetable = (
        db.query(Timetable)
        .filter(
            Timetable.course == course,
            Timetable.division == division,
            Timetable.day == day
        )
        .all()
    )

    if not timetable:

        return {
            "message": "No timetable found for the given details."
        }

    return {
        "course": course,
        "division": division,
        "day": day,
        "timetable": [
            {
                "start_time": item.start_time,
                "end_time": item.end_time,
                "subject": item.subject,
                "teacher": item.teacher,
                "room": item.room,
                "lecture_type": item.lecture_type
            }
            for item in timetable
        ]
    }