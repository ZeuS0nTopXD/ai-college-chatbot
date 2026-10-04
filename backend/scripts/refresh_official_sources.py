"""Refresh searchable copies of public VSIT pages.

Run from a scheduler (or manually) with the same environment as the app:
``python -m backend.scripts.refresh_official_sources``.
Only public pages are fetched; no login or student data is involved.
"""

import re
from html import unescape
from uuid import uuid4

import requests

from backend.config import Settings
from backend.database.database import Base, SessionLocal, configure_database
from backend.models.document import Document, DocumentChunk
from backend.services.document_service import chunk_pages, ExtractedPage


SOURCE_PAGES = {
    "VSIT Admissions": ("ADMISSIONS", "https://vsit.edu.in/admission/"),
    "VSIT Placements": ("PLACEMENTS", "https://vsit.edu.in/placements/"),
    "VSIT Library": ("LIBRARY", "https://vsit.edu.in/library/"),
    "VSIT News Updates": ("ACADEMIC", "https://vsit.edu.in/news-update/"),
    "VSIT Results": ("RESULT", "https://vsit.edu.in/result/"),
    "VSIT Student Life": ("VSIT", "https://vsit.edu.in/student-life/"),
    "VSIT Contact": ("VSIT", "https://vsit.edu.in/contact-us/"),
    "VSIT BMS Admissions": ("ADMISSIONS", "https://vsit.edu.in/admission-bms/"),
    "VSIT BMS Programme": ("ACADEMIC", "https://vsit.edu.in/b-m-s/"),
    "VSIT BSc Computer Science": ("ACADEMIC", "https://vsit.edu.in/bsc-cs-se/"),
    "VSIT MCom Business Management": ("ACADEMIC", "https://vsit.edu.in/m-com-bm/"),
    "VSIT Student Grievance Committee": ("ACADEMIC", "https://vsit.edu.in/student-grievance-redressal-committee/"),
    "VSIT Academics": ("ACADEMIC", "https://vsit.edu.in/academic/"),
    "VSIT BSc IT Syllabus": ("ACADEMIC", "https://vsit.edu.in/syllabus-b-sc-it/"),
    "VSIT MSc Data Science Syllabus": ("ACADEMIC", "https://vsit.edu.in/syllabus-m-sc-ds-ai/"),
    "VSIT AQAR 2023-24": ("ACADEMIC", "https://vsit.edu.in/aqar-2023-24-data/"),
    "VSIT Examination Notices": ("ACADEMIC", "https://vsit.edu.in/examinations-2024-winter-session/"),
}


def _readable_text(html: str) -> str:
    html = re.sub(r"<(script|style|noscript)[^>]*>.*?</\1>", " ", html, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", unescape(text)).strip()


def refresh_sources(db=None) -> int:
    owns_session = db is None
    if owns_session:
        settings = Settings.from_env()
        engine = configure_database(settings.database_url)
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
    refreshed = 0
    try:
        for title, (category, url) in SOURCE_PAGES.items():
            response = requests.get(url, timeout=20, headers={"User-Agent": "VSIT-Student-Assistant/1.0"})
            response.raise_for_status()
            text = _readable_text(response.text)
            if len(text) < 120:
                continue
            document = db.query(Document).filter(Document.title == title).first()
            if document:
                document.category = category
                document.status = "ready"
                document.chunks.clear()
            else:
                document = Document(title=title, category=category, filename=f"{title.lower().replace(' ', '-')}.html",
                                    stored_filename=f"official-{uuid4().hex}.html", content_type="text/html",
                                    page_count=1, status="ready")
                db.add(document)
                db.flush()
            for chunk in chunk_pages([ExtractedPage(page_number=1, text=text)]):
                document.chunks.append(DocumentChunk(page_number=chunk.page_number, chunk_index=chunk.chunk_index,
                                                     content=chunk.content))
            refreshed += 1
        db.commit()
        return refreshed
    finally:
        if owns_session:
            db.close()


if __name__ == "__main__":
    print(f"Refreshed {refresh_sources()} official VSIT source documents.")
