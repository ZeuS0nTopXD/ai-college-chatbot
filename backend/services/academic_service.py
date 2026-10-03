import re
from datetime import datetime

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from backend.models.academic import AcademicEvent


def list_published_events(
    db: Session,
    event_type: str | None = None,
    course: str | None = None,
    semester: str | None = None,
    from_date: datetime | None = None,
) -> list[AcademicEvent]:
    query = db.query(AcademicEvent).filter(AcademicEvent.is_published.is_(True))

    if event_type:
        query = query.filter(func.lower(AcademicEvent.event_type) == event_type.lower())
    if course:
        query = query.filter(
            or_(
                AcademicEvent.course.is_(None),
                func.lower(AcademicEvent.course) == course.lower(),
            )
        )
    if semester:
        query = query.filter(
            or_(
                AcademicEvent.semester.is_(None),
                func.lower(AcademicEvent.semester) == semester.lower(),
            )
        )
    if from_date:
        query = query.filter(
            or_(
                AcademicEvent.starts_at >= from_date,
                AcademicEvent.ends_at >= from_date,
            )
        )

    return query.order_by(AcademicEvent.starts_at.asc(), AcademicEvent.id.asc()).all()


def _tokens(value: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", value.lower()))


COURSE_ALIASES = {
    "bsc it": ("bsc it", "b.sc it", "b.sc. it", "information technology"),
    "bsc cs": ("bsc cs", "b.sc cs", "b.sc. cs", "computer science"),
    "data science": ("data science", "bsc ds", "b.sc ds", "b.sc. ds"),
}


def _canonical_course(value: str) -> str:
    normalized = " ".join(re.sub(r"[^a-z0-9]+", " ", value.lower()).split())
    for canonical, aliases in COURSE_ALIASES.items():
        if any(
            " ".join(re.sub(r"[^a-z0-9]+", " ", alias).split()) in normalized
            for alias in aliases
        ):
            return canonical
    return normalized


def _requested_course(message: str) -> str | None:
    canonical_message = _canonical_course(message)
    for course in COURSE_ALIASES:
        if course in canonical_message:
            return course
    return None


def answer_academic_question(db: Session, message: str) -> dict | None:
    query_text = " ".join(message.lower().split())
    query_tokens = _tokens(query_text)
    requested_course = _requested_course(query_text)
    semester_match = re.search(r"\b(?:semester|sem)\s*([1-9][0-9]*)\b", query_text)
    requested_semester = semester_match.group(1) if semester_match else None
    events = list_published_events(db, from_date=datetime.now())
    ranked = []

    for event in events:
        if (
            requested_course
            and event.course
            and _canonical_course(event.course) != requested_course
        ):
            continue
        if (
            requested_semester
            and event.semester
            and event.semester.strip().lower() != requested_semester
        ):
            continue
        score = len(
            query_tokens
            & _tokens(
                " ".join(
                    filter(
                        None,
                        [event.title, event.description, event.event_type],
                    )
                )
            )
        )
        if event.event_type.lower() == "examination" and query_tokens & {
            "exam",
            "exams",
            "examination",
        }:
            score += 5
        if event.course and event.course.lower() in query_text:
            score += 5
        if event.semester and re.search(
            rf"\b(?:semester|sem)\s*{re.escape(event.semester.lower())}\b",
            query_text,
        ):
            score += 5
        if score:
            ranked.append((score, event))

    if not ranked:
        return None

    ranked.sort(key=lambda pair: (-pair[0], pair[1].starts_at, pair[1].id))
    event = ranked[0][1]
    date_text = f"{event.starts_at.day} {event.starts_at.strftime('%B %Y')}"
    time_text = event.starts_at.strftime("%I:%M %p").lstrip("0")
    response = f"📅 {event.title} is scheduled for {date_text} at {time_text}."
    if event.location:
        response += f" Location: {event.location}."

    return {
        "bot_response": response,
        "event_id": event.id,
        "resource_url": event.resource_url,
    }
