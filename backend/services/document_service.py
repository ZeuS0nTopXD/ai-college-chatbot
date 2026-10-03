import re
from collections import Counter
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader
from sqlalchemy.orm import Session

from backend.models.document import Document, DocumentChunk


STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "at",
    "be",
    "by",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "the",
    "to",
    "what",
    "when",
    "where",
    "who",
    "with",
}


class DocumentValidationError(ValueError):
    pass


@dataclass(frozen=True)
class ExtractedPage:
    page_number: int
    text: str


@dataclass(frozen=True)
class ChunkInput:
    page_number: int
    chunk_index: int
    content: str


@dataclass(frozen=True)
class SearchHit:
    document_id: int
    title: str
    category: str
    page: int
    excerpt: str
    score: float


def extract_document(filename: str, content: bytes) -> list[ExtractedPage]:
    suffix = Path(filename).suffix.lower()
    if suffix not in {".pdf", ".txt"}:
        raise DocumentValidationError("Only PDF and TXT documents are supported.")

    if suffix == ".txt":
        try:
            text = content.decode("utf-8-sig").strip()
        except UnicodeDecodeError as exc:
            raise DocumentValidationError("The text document must use UTF-8 encoding.") from exc
        if not text:
            raise DocumentValidationError("The document contains no readable text.")
        return [ExtractedPage(page_number=1, text=text)]

    try:
        reader = PdfReader(BytesIO(content))
        pages = [
            ExtractedPage(page_number=index, text=(page.extract_text() or "").strip())
            for index, page in enumerate(reader.pages, start=1)
        ]
    except Exception as exc:
        raise DocumentValidationError("The PDF could not be read.") from exc

    pages = [page for page in pages if page.text]
    if not pages:
        raise DocumentValidationError("The document contains no readable text.")
    return pages


def chunk_pages(
    pages: list[ExtractedPage],
    max_chars: int = 1200,
    overlap_chars: int = 150,
) -> list[ChunkInput]:
    chunks = []
    chunk_index = 0
    for page in pages:
        text = re.sub(r"\s+", " ", page.text).strip()
        start = 0
        while start < len(text):
            end = min(start + max_chars, len(text))
            if end < len(text):
                break_at = text.rfind(" ", start, end)
                if break_at > start:
                    end = break_at
            content = text[start:end].strip()
            if content:
                chunks.append(
                    ChunkInput(
                        page_number=page.page_number,
                        chunk_index=chunk_index,
                        content=content,
                    )
                )
                chunk_index += 1
            if end >= len(text):
                break
            start = max(end - overlap_chars, start + 1)
    return chunks


def _tokens(text: str) -> list[str]:
    return [
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if token not in STOP_WORDS and len(token) > 1
    ]


def search_documents(
    db: Session,
    query: str,
    limit: int = 4,
    min_score: float = 0.12,
) -> list[SearchHit]:
    query_tokens = _tokens(query)
    if not query_tokens:
        return []
    query_terms = set(query_tokens)
    rows = (
        db.query(DocumentChunk, Document)
        .join(Document, Document.id == DocumentChunk.document_id)
        .filter(Document.status == "ready")
        .all()
    )
    ranked = []
    for chunk, document in rows:
        counts = Counter(_tokens(chunk.content))
        matched = query_terms & counts.keys()
        if not matched:
            continue
        coverage = len(matched) / len(query_terms)
        frequency = sum(min(counts[term], 3) for term in matched) / (
            3 * len(query_terms)
        )
        score = round((coverage * 0.85) + (frequency * 0.15), 4)
        if score < min_score:
            continue
        ranked.append(
            SearchHit(
                document_id=document.id,
                title=document.title,
                category=document.category,
                page=chunk.page_number,
                excerpt=chunk.content,
                score=score,
            )
        )

    ranked.sort(key=lambda hit: (-hit.score, hit.document_id, hit.page))
    return ranked[:limit]
