from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.dependencies import get_db
from backend.models.academic import AcademicEvent
from backend.models.faculty import Faculty
from backend.models.knowledge import KnowledgeBase
from backend.models.office import Office
from backend.schemas.academic import (
    AcademicEventCreate,
    AcademicEventRead,
    AcademicEventUpdate,
)
from backend.schemas.admin import (
    FacultyCreate,
    FacultyRead,
    FacultyUpdate,
    OfficeCreate,
    OfficeRead,
    OfficeUpdate,
)
from backend.schemas.knowledge import KnowledgeCreate, KnowledgeRead, KnowledgeUpdate
from backend.security import require_admin
from backend.scripts.refresh_official_sources import refresh_sources


router = APIRouter(
    prefix="/api/admin",
    tags=["administration"],
    dependencies=[Depends(require_admin)],
)


@router.post("/refresh-sources")
def refresh_public_sources(db: Session = Depends(get_db)):
    """Refresh searchable public VSIT pages without touching private data."""
    try:
        return {"refreshed_documents": refresh_sources(db)}
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Official source refresh failed.") from exc


def _get_or_404(db: Session, model, record_id: int):
    record = db.get(model, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found.")
    return record


def _save(db: Session, record):
    try:
        db.add(record)
        db.commit()
        db.refresh(record)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unable to save record.") from exc
    return record


def _update(db: Session, record, payload):
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    return _save(db, record)


def _delete(db: Session, record):
    try:
        db.delete(record)
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unable to delete record.") from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/academics", response_model=list[AcademicEventRead])
def list_academics(db: Session = Depends(get_db)):
    return db.query(AcademicEvent).order_by(AcademicEvent.id).all()


@router.post(
    "/academics",
    response_model=AcademicEventRead,
    status_code=status.HTTP_201_CREATED,
)
def create_academic(payload: AcademicEventCreate, db: Session = Depends(get_db)):
    return _save(db, AcademicEvent(**payload.model_dump()))


@router.patch("/academics/{record_id}", response_model=AcademicEventRead)
def update_academic(
    record_id: int,
    payload: AcademicEventUpdate,
    db: Session = Depends(get_db),
):
    return _update(db, _get_or_404(db, AcademicEvent, record_id), payload)


@router.delete("/academics/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_academic(record_id: int, db: Session = Depends(get_db)):
    return _delete(db, _get_or_404(db, AcademicEvent, record_id))


@router.get("/knowledge", response_model=list[KnowledgeRead])
def list_knowledge(db: Session = Depends(get_db)):
    return db.query(KnowledgeBase).order_by(KnowledgeBase.id).all()


@router.post(
    "/knowledge",
    response_model=KnowledgeRead,
    status_code=status.HTTP_201_CREATED,
)
def create_knowledge(payload: KnowledgeCreate, db: Session = Depends(get_db)):
    return _save(db, KnowledgeBase(**payload.model_dump()))


@router.patch("/knowledge/{record_id}", response_model=KnowledgeRead)
def update_knowledge(
    record_id: int,
    payload: KnowledgeUpdate,
    db: Session = Depends(get_db),
):
    return _update(db, _get_or_404(db, KnowledgeBase, record_id), payload)


@router.delete("/knowledge/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_knowledge(record_id: int, db: Session = Depends(get_db)):
    return _delete(db, _get_or_404(db, KnowledgeBase, record_id))


@router.get("/faculty", response_model=list[FacultyRead])
def list_faculty(db: Session = Depends(get_db)):
    return db.query(Faculty).order_by(Faculty.id).all()


@router.post(
    "/faculty",
    response_model=FacultyRead,
    status_code=status.HTTP_201_CREATED,
)
def create_faculty(payload: FacultyCreate, db: Session = Depends(get_db)):
    return _save(db, Faculty(**payload.model_dump()))


@router.patch("/faculty/{record_id}", response_model=FacultyRead)
def update_faculty(
    record_id: int,
    payload: FacultyUpdate,
    db: Session = Depends(get_db),
):
    return _update(db, _get_or_404(db, Faculty, record_id), payload)


@router.delete("/faculty/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_faculty(record_id: int, db: Session = Depends(get_db)):
    return _delete(db, _get_or_404(db, Faculty, record_id))


@router.get("/offices", response_model=list[OfficeRead])
def list_offices(db: Session = Depends(get_db)):
    return db.query(Office).order_by(Office.id).all()


@router.post(
    "/offices",
    response_model=OfficeRead,
    status_code=status.HTTP_201_CREATED,
)
def create_office(payload: OfficeCreate, db: Session = Depends(get_db)):
    return _save(db, Office(**payload.model_dump()))


@router.patch("/offices/{record_id}", response_model=OfficeRead)
def update_office(
    record_id: int,
    payload: OfficeUpdate,
    db: Session = Depends(get_db),
):
    return _update(db, _get_or_404(db, Office, record_id), payload)


@router.delete("/offices/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_office(record_id: int, db: Session = Depends(get_db)):
    return _delete(db, _get_or_404(db, Office, record_id))
