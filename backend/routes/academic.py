from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.dependencies import get_db
from backend.schemas.academic import AcademicEventRead
from backend.services.academic_service import list_published_events


router = APIRouter(prefix="/api/academics", tags=["academics"])


@router.get("", response_model=list[AcademicEventRead])
def get_academic_events(
    event_type: str | None = None,
    course: str | None = None,
    semester: str | None = None,
    from_date: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return list_published_events(
        db,
        event_type=event_type,
        course=course,
        semester=semester,
        from_date=from_date,
    )
