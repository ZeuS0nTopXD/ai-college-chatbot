from pathlib import Path

import pytest

from backend.database.database import SessionLocal
from backend.models.document import Document, DocumentChunk
from backend.models.knowledge import KnowledgeBase


FIXTURE = Path(__file__).parent / "fixtures" / "vsit_notice.txt"


def admin_headers(client):
    response = client.post(
        "/api/auth/login",
        json={"password": "test-admin-password"},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def upload_notice(client, filename="vsit_notice.txt", content=None):
    body = FIXTURE.read_bytes() if content is None else content
    return client.post(
        "/api/admin/documents",
        headers=admin_headers(client),
        data={"title": "Semester Examination Notice", "category": "examination"},
        files={"file": (filename, body)},
    )


def database_counts():
    db = SessionLocal()
    try:
        return db.query(Document).count(), db.query(DocumentChunk).count()
    finally:
        db.close()


def test_text_upload_creates_page_aware_chunks(client):
    response = upload_notice(client)

    assert response.status_code == 201
    assert response.json()["title"] == "Semester Examination Notice"
    assert response.json()["page_count"] == 1
    db = SessionLocal()
    try:
        chunks = db.query(DocumentChunk).order_by(DocumentChunk.chunk_index).all()
        assert chunks
        assert {chunk.page_number for chunk in chunks} == {1}
        assert "15 February 2027" in " ".join(chunk.content for chunk in chunks)
    finally:
        db.close()


def test_search_returns_title_page_and_relevant_excerpt(client):
    upload_notice(client)

    response = client.post(
        "/api/documents/search",
        json={"query": "When must semester examination forms be submitted?"},
    )

    assert response.status_code == 200
    hit = response.json()["hits"][0]
    assert hit["title"] == "Semester Examination Notice"
    assert hit["page"] == 1
    assert "15 February 2027" in hit["excerpt"]
    assert hit["score"] > 0


def test_search_normalizes_case_and_punctuation(client):
    upload_notice(client)

    response = client.post(
        "/api/documents/search",
        json={"query": "EXAMINATION-CELL, forms?!"},
    )

    assert response.status_code == 200
    assert response.json()["hits"][0]["page"] == 1


def test_search_without_overlap_returns_no_hits(client):
    upload_notice(client)

    response = client.post(
        "/api/documents/search",
        json={"query": "hostel bus route"},
    )

    assert response.status_code == 200
    assert response.json() == {"hits": []}


def test_chat_uses_cited_document_when_it_has_a_reliable_match(client):
    upload_notice(client)

    response = client.post(
        "/chat",
        json={"message": "What is the deadline for examination forms?"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "DOCUMENT"
    assert "15 February 2027" in body["bot_response"]
    assert body["sources"][0]["title"] == "Semester Examination Notice"
    assert body["sources"][0]["page"] == 1


def test_verified_knowledge_beats_a_weak_document_match(client):
    db = SessionLocal()
    try:
        db.add(
            KnowledgeBase(
                category="VSIT",
                topic="attendance",
                question="What is the attendance requirement?",
                answer="The verified attendance requirement is 75 percent.",
            )
        )
        document = Document(
            title="General Student Guide",
            category="general",
            filename="guide.txt",
            stored_filename="guide.txt",
            page_count=1,
            status="ready",
        )
        db.add(document)
        db.flush()
        db.add(
            DocumentChunk(
                document_id=document.id,
                page_number=1,
                chunk_index=0,
                content="Students should review the attendance guide regularly.",
            )
        )
        db.commit()
    finally:
        db.close()

    response = client.post(
        "/chat",
        json={"message": "What is the attendance requirement?"},
    )

    assert response.status_code == 200
    assert response.json()["category"] == "VSIT"
    assert response.json()["bot_response"] == (
        "The verified attendance requirement is 75 percent."
    )


def test_deleting_document_removes_chunks_and_file(client, settings):
    uploaded = upload_notice(client).json()
    db = SessionLocal()
    try:
        stored_filename = db.get(Document, uploaded["id"]).stored_filename
    finally:
        db.close()
    stored_path = settings.document_storage_path / stored_filename
    assert stored_path.exists()

    response = client.delete(
        f"/api/admin/documents/{uploaded['id']}",
        headers=admin_headers(client),
    )

    assert response.status_code == 204
    assert database_counts() == (0, 0)
    assert not stored_path.exists()


@pytest.mark.parametrize(
    "filename,content,expected_status",
    [
        ("notice.docx", b"unsupported", 400),
        ("large.txt", b"x" * (1024 * 1024 + 1), 413),
        ("empty.txt", b"   \n\t", 400),
        ("broken.pdf", b"this is not a PDF", 400),
    ],
    ids=["unsupported", "oversized", "empty-text", "corrupt-pdf"],
)
def test_invalid_uploads_leave_no_database_or_file_residue(
    client,
    settings,
    filename,
    content,
    expected_status,
):
    response = upload_notice(client, filename=filename, content=content)

    assert response.status_code == expected_status
    assert database_counts() == (0, 0)
    assert not settings.document_storage_path.exists() or not any(
        settings.document_storage_path.iterdir()
    )
