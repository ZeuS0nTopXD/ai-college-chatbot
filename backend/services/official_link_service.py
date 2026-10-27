"""Match clear student resource requests to verified public VSIT links."""

import re

from backend.data.official_links import OFFICIAL_LINKS
from backend.data.official_vsit_data import OFFICIAL_KNOWLEDGE_DATA


LINKS_BY_TITLE = {item["title"]: item for item in OFFICIAL_LINKS}


def answer_official_source_question(message: str) -> dict | None:
    text = " ".join(re.sub(r"[^a-z0-9]+", " ", message.lower()).split())
    compact = text.replace(" ", "")
    asks_for_link = bool(re.search(r"\b(where|find|link|download|website|page|open|show|access|browse)\b", text))
    title = None
    verified_answer = None

    if re.search(r"\b(office|cell|student section)\b", text):
        return None

    if re.search(r"\b(syllabus|curriculum)\b", text):
        if "msc" in compact and "datascience" in compact:
            title = "M.Sc. Data Science & AI syllabus"
        elif "msc" in compact and ("it" in text.split() or "informationtechnology" in compact):
            title = "M.Sc. Information Technology syllabus"
        elif "bsc" in compact and "datascience" in compact:
            title = "B.Sc. Data Science syllabus"
        elif "bsc" in compact and ("aiml" in compact or "artificialintelligence" in compact):
            title = "B.Sc. Computer Science (AI & ML) syllabus"
        elif "bsc" in compact and ("it" in text.split() or "informationtechnology" in compact):
            title = "B.Sc. Information Technology syllabus"
        else:
            title = "Programme brochures"
    elif re.search(r"\b(brochure|brochures|prospectus)\b", text):
        title = "Programme brochures"
    elif asks_for_link and re.search(r"\b(transcript|transcripts)\b", text):
        title = "Transcript applications"
    elif asks_for_link and re.search(r"\b(exam|exams|examination|notice|notices|circular|circulars)\b", text):
        if "regular" in text and "commencement" in text:
            title = "Winter 2026 regular examination commencement notice"
        else:
            title = "News Update and examination notices"
    elif asks_for_link and "library" in text:
        title = "Library hours and services"
        wants_hours = bool(re.search(r"\b(?:when|what time|hours?|timings?|open|opening)\b", text))
        target_question = "timings" if wants_hours else "where"
        verified_answer = next(
            (
                item["answer"]
                for item in OFFICIAL_KNOWLEDGE_DATA
                if item["category"] == "LIBRARY"
                and target_question in item["question"].lower()
            ),
            None,
        )
    elif asks_for_link and re.search(r"\b(admission|admissions)\b", text):
        title = "Admissions"
    elif asks_for_link and re.search(r"\b(placement|placements)\b", text):
        title = "Placements"
    elif asks_for_link and re.search(r"\b(contact|address|directions)\b", text):
        title = "Contact VSIT"

    if title is None:
        return None
    source = LINKS_BY_TITLE[title]
    return {
        "bot_response": verified_answer or f"{source['description']} Open the VSIT website for the full, current information.",
        "resource_url": source["url"],
    }
