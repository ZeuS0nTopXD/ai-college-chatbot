from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.dependencies import get_db
from backend.models.feedback import Feedback
from backend.models.student import StudentUser
from backend.schemas.feedback import FeedbackCreate, FeedbackRead
from backend.security import require_student


router = APIRouter(prefix="/api/feedback", tags=["feedback"])


def _read_feedback(record: Feedback, student: StudentUser) -> FeedbackRead:
    return FeedbackRead(
        id=record.id,
        user_id=record.user_id,
        student_name=student.name,
        student_email=student.email,
        rating=record.rating,
        message=record.message,
        context=record.context,
        status=record.status,
        created_at=record.created_at,
    )


@router.post("", response_model=FeedbackRead, status_code=status.HTTP_201_CREATED)
def create_feedback(
    payload: FeedbackCreate,
    student_id: int = Depends(require_student),
    db: Session = Depends(get_db),
):
    student = db.get(StudentUser, student_id)
    if student is None:
        raise HTTPException(status_code=401, detail="Student account no longer exists.")
    record = Feedback(
        user_id=student.id,
        rating=payload.rating,
        message=payload.message.strip(),
        context=payload.context.strip() if payload.context else None,
        status="new",
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return _read_feedback(record, student)
