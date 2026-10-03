from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.database import SessionLocal
from backend.models.result import Result


router = APIRouter()


# Database connection
def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# Get all results for a course
@router.get("/result/{course}")
def get_results_by_course(
    course: str,
    db: Session = Depends(get_db)
):

    results = (
        db.query(Result)
        .filter(Result.course == course.upper())
        .all()
    )

    if not results:

        return {
            "message": f"No result information found for {course}."
        }

    return {
        "course": course,
        "results": [
            {
                "semester": item.semester,
                "batch": item.batch,
                "year": item.year,
                "title": item.title,
                "url": item.url
            }
            for item in results
        ]
    }


# Get result for a course + semester
@router.get("/result/{course}/{semester}")
def get_result_by_semester(
    course: str,
    semester: str,
    db: Session = Depends(get_db)
):

    result = (
        db.query(Result)
        .filter(
            Result.course == course.upper(),
            Result.semester == semester
        )
        .first()
    )

    if not result:

        return {
            "message": (
                f"No result found for {course} Semester {semester}."
            )
        }

    return {
        "course": course,
        "semester": semester,
        "batch": result.batch,
        "year": result.year,
        "title": result.title,
        "url": result.url
    }
