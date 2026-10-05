from pathlib import Path
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    Response,
    UploadFile,
    status,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.dependencies import get_db
from backend.data.official_links import OFFICIAL_LINKS
from backend.models.document import Document, DocumentChunk
from backend.schemas.document import (
    DocumentRead,
    DocumentSearchRequest,
    DocumentSearchResponse,
)
from backend.security import require_admin
from backend.services.document_service import (
    DocumentValidationError,
    chunk_pages,
    extract_document,
    search_documents,
)


public_router = APIRouter(prefix="/api/documents", tags=["documents"])
admin_router = APIRouter(
    prefix="/api/admin/documents",
    tags=["administration"],
    dependencies=[Depends(require_admin)],
)


@public_router.get("/official-sources")
def list_official_sources(section: str | None = None):
    if section:
        return [item for item in OFFICIAL_LINKS if section in item["sections"]]
    return OFFICIAL_LINKS


@public_router.get("", response_model=list[DocumentRead])
def list_public_documents(db: Session = Depends(get_db)):
    return (
        db.query(Document)
        .filter(Document.status == "ready")
        .order_by(Document.id)
        .all()
    )


@public_router.post("/search", response_model=DocumentSearchResponse)
def search_public_documents(
    payload: DocumentSearchRequest,
    db: Session = Depends(get_db),
):
    return {"hits": search_documents(db, payload.query, limit=payload.limit)}


@admin_router.get("", response_model=list[DocumentRead])
def list_admin_documents(db: Session = Depends(get_db)):
    return db.query(Document).order_by(Document.id).all()


@admin_router.post("", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def upload_document(
    request: Request,
    title: str = Form(min_length=1, max_length=200),
    category: str = Form(min_length=1, max_length=100),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    filename = Path(file.filename or "").name
    content = await file.read()
    settings = request.app.state.settings
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="Document exceeds the upload limit.")

    try:
        pages = extract_document(filename, content)
        chunks = chunk_pages(pages)
    except DocumentValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    storage_path = settings.document_storage_path
    storage_path.mkdir(parents=True, exist_ok=True)
    stored_filename = f"{uuid4().hex}{Path(filename).suffix.lower()}"
    stored_path = storage_path / stored_filename

    document = Document(
        title=title.strip(),
        category=category.strip(),
        filename=filename,
        stored_filename=stored_filename,
        content_type=file.content_type,
        page_count=len(pages),
        status="ready",
    )
    try:
        stored_path.write_bytes(content)
        db.add(document)
        db.flush()
        db.add_all(
            DocumentChunk(
                document_id=document.id,
                page_number=chunk.page_number,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
            )
            for chunk in chunks
        )
        db.commit()
        db.refresh(document)
    except (OSError, SQLAlchemyError) as exc:
        db.rollback()
        stored_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail="Unable to store document.") from exc
    return document


@admin_router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    stored_path = request.app.state.settings.document_storage_path / document.stored_filename
    try:
        db.delete(document)
        db.commit()
        stored_path.unlink(missing_ok=True)
    except (OSError, SQLAlchemyError) as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unable to delete document.") from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
