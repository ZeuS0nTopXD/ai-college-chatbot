"""
VSIT Student Assistant - Timetable Service

This service is written for the CURRENT timetable table structure:

id
academic_year
semester
effective_from
course
division
day
start_time
end_time
subject_code
subject_name
room
session_type
teacher_names
created_at

IMPORTANT:
The SQLAlchemy Timetable model must use these same column names.
"""

import re
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.models.timetable import Timetable


# ============================================================
# CONSTANTS
# ============================================================

DEFAULT_COURSE = "B.Sc. Information Technology"

COURSE_ALIASES = {
    "tyit": DEFAULT_COURSE,
    "ty it": DEFAULT_COURSE,
    "third year it": DEFAULT_COURSE,
    "third year information technology": DEFAULT_COURSE,
    "third year information technology": DEFAULT_COURSE,
    "syit": DEFAULT_COURSE,
    "sy it": DEFAULT_COURSE,
    "second year it": DEFAULT_COURSE,
    "second year information technology": DEFAULT_COURSE,
    "fyit": DEFAULT_COURSE,
    "fy it": DEFAULT_COURSE,
    "first year it": DEFAULT_COURSE,
    "first year information technology": DEFAULT_COURSE,
}

DAYS = {
    "monday": "Monday",
    "tuesday": "Tuesday",
    "wednesday": "Wednesday",
    "thursday": "Thursday",
    "friday": "Friday",
    "saturday": "Saturday",
    "sunday": "Sunday",
}

SUBJECT_ALIASES = {
    ".net": ".NET",
    "dot net": ".NET",
    "dotnet": ".NET",
    "iot": "IOT",
    "internet of things": "IOT",
    "iks": "IKS",
    "indian knowledge systems": "IKS",
    "ai": "AI",
    "artificial intelligence": "AI",
    "mern": "MERN",
    "jira": "JIRA",
    "ej": "EJ",
    "ira": "IRA",
    "ap": "AP",
    "dbms": "DBMS",
    "database management system": "DBMS",
    "os": "OS",
    "operating system": "OS",
    "cn": "CN",
    "computer networks": "CN",
    "computer network": "CN",
}

TIMETABLE_KEYWORDS = [
    "timetable",
    "time table",
    "schedule",
    "class schedule",
    "class timetable",
    "lecture schedule",
    "lecture timetable",
    "today class",
    "today classes",
    "today's class",
    "today's classes",
    "tomorrow class",
    "tomorrow classes",
    "tomorrow's class",
    "tomorrow's classes",
    "what classes",
    "which classes",
    "class timing",
    "class timings",
    "lecture timing",
    "lecture timings",
    "period",
    "periods",
]

TIMETABLE_INTENT_WORDS = [
    "timetable",
    "time table",
    "schedule",
    "class",
    "classes",
    "lecture",
    "lectures",
    "period",
    "periods",
    "today",
    "tomorrow",
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
    "room",
    "lab",
    "practical",
    "when is",
    "what time",
]


# ============================================================
# TEXT HELPERS
# ============================================================

def normalize_message(message: str) -> str:
    if not message:
        return ""
    return re.sub(r"\s+", " ", message.lower().strip())


def normalize_course(course: str | None) -> str:
    if not course:
        return DEFAULT_COURSE

    value = normalize_message(course)

    if value in COURSE_ALIASES:
        return COURSE_ALIASES[value]

    if "information technology" in value:
        return DEFAULT_COURSE

    return course.strip()


def course_display_name(course: str | None) -> str:
    if not course:
        return "TYIT"

    value = normalize_message(course)

    if "information technology" in value:
        return "TYIT"

    return course.strip()


def normalize_day(day: str | None) -> str | None:
    if not day:
        return None

    value = normalize_message(day)

    if value in DAYS:
        return DAYS[value]

    return day.strip().capitalize()


def normalize_subject(subject: str | None) -> str | None:
    if not subject:
        return None

    value = normalize_message(subject)

    if value in SUBJECT_ALIASES:
        return SUBJECT_ALIASES[value]

    return subject.strip()


def clean_value(value) -> str | None:
    if value is None:
        return None

    value = str(value).strip()

    return value if value else None


def get_field(item, *names):
    for name in names:
        value = getattr(item, name, None)
        if value is not None and str(value).strip():
            return value
    return None


# ============================================================
# QUESTION DETECTION
# ============================================================

def is_timetable_question(question: str) -> bool:
    """
    Detect timetable/class questions without using unsafe substring
    matching. This prevents words such as 'available' from being
    interpreted as 'lab'.
    """
    if not question:
        return False

    q = normalize_message(question)

    # Direct timetable phrases.
    for keyword in TIMETABLE_KEYWORDS:
        if re.search(r"(?<!\w)" + re.escape(keyword) + r"(?!\w)", q):
            return True

    # Course/division context.
    if re.search(r"\b(?:fy|sy|ty)\s*it\b", q):
        return True

    if re.search(r"\bdivision\s*[a-e]\b", q):
        return True

    if re.search(r"\bdiv\s*[a-e]\b", q):
        return True

    # Common teacher/subject timetable questions.
    if re.search(r"\bwho\s+(teaches|teach)\b", q):
        return True

    if re.search(r"\bteacher\s+of\b", q):
        return True

    if re.search(r"\bwho\s+is\s+teaching\b", q):
        return True

    if re.search(r"\bwhich\s+(faculty|professor)\s+teaches\b", q):
        return True

    # Subject + time/room questions.
    if (
        re.search(r"\bwhen\s+is\b", q)
        or re.search(r"\bwhat\s+time\b", q)
        or re.search(r"\bwhich\s+room\b", q)
        or re.search(r"\broom\s+for\b", q)
    ):
        return True

    return False


# ============================================================
# COURSE / DIVISION / DAY EXTRACTION
# ============================================================

def extract_timetable_details(question: str):
    q = normalize_message(question)

    result = {
        "course": None,
        "division": None,
        "day": None,
    }

    # Course.
    course_patterns = [
        r"\bty\s*it\b",
        r"\bsy\s*it\b",
        r"\bfy\s*it\b",
        r"\bthird year\b",
        r"\bsecond year\b",
        r"\bfirst year\b",
        r"\bb\.?\s*sc\.?\s+information technology\b",
        r"\binformation technology\b",
    ]

    for pattern in course_patterns:
        match = re.search(pattern, q)
        if match:
            result["course"] = normalize_course(match.group(0))
            break

    # Division A-E.
    division_patterns = [
        r"\bdivision\s*([a-e])\b",
        r"\bdiv\s*([a-e])\b",
    ]

    for pattern in division_patterns:
        match = re.search(pattern, q)
        if match:
            result["division"] = match.group(1).upper()
            break

    # "TYIT A", "TY IT B", etc.
    if not result["division"]:
        match = re.search(
            r"\b(?:fy|sy|ty)\s*it\s*[-]?\s*([a-e])\b",
            q,
        )
        if match:
            result["division"] = match.group(1).upper()

    # Day.
    for key, display in DAYS.items():
        if re.search(r"\b" + re.escape(key) + r"\b", q):
            result["day"] = display
            break

    return result


# ============================================================
# RELATIVE DAY
# ============================================================

def get_today_name():
    return datetime.now().strftime("%A")


def get_next_day_name():
    return (datetime.now() + timedelta(days=1)).strftime("%A")


def detect_relative_day(message: str):
    q = normalize_message(message)

    if re.search(r"\btomorrow\b", q):
        return get_next_day_name()

    if re.search(r"\btoday\b", q):
        return get_today_name()

    return None


# ============================================================
# LECTURE TYPE
# ============================================================

def detect_lecture_type(message: str):
    q = normalize_message(message)

    if re.search(r"\b(?:practical|practicals|lab|laboratory)\b", q):
        return "Practical"

    if re.search(r"\btheory\b", q):
        return "Theory"

    return None


# ============================================================
# INTENT
# ============================================================

def get_timetable_intent(message: str):
    q = normalize_message(message)

    if re.search(r"\bwho\s+(teaches|teach)\b", q):
        return "TEACHER"

    if "teacher of" in q or "who is teaching" in q:
        return "TEACHER"

    if re.search(r"\bwhich\s+(faculty|professor)\s+teaches\b", q):
        return "TEACHER"

    if (
        "what subjects does" in q
        or "which subjects does" in q
        or "subjects taught by" in q
    ):
        return "TEACHER_SUBJECT"

    if (
        "which room" in q
        or "room for" in q
        or "where is the" in q and "lab" in q
        or "where is" in q and "class" in q
    ):
        return "ROOM"

    if (
        "when is" in q
        or "when does" in q
        or "what time" in q
        or "time of" in q
    ):
        return "SUBJECT_TIME"

    if (
        "timetable" in q
        or "time table" in q
        or "class schedule" in q
        or "schedule" in q
        or "what classes" in q
        or "which classes" in q
        or "today classes" in q
        or "tomorrow classes" in q
    ):
        return "FULL_TIMETABLE"

    return "FULL_TIMETABLE"


# ============================================================
# SUBJECT EXTRACTION
# ============================================================

def extract_subject(message: str, timetable=None):
    q = normalize_message(message)

    # First use actual DB subjects. Longest names first.
    if timetable:
        subjects = set()

        for item in timetable:
            subject = get_field(item, "subject_name", "subject_code", "subject")
            if subject:
                subjects.add(str(subject).strip())

        for subject in sorted(subjects, key=len, reverse=True):
            if normalize_message(subject) in q:
                return subject

    # Then aliases.
    for phrase, subject in sorted(
        SUBJECT_ALIASES.items(),
        key=lambda x: len(x[0]),
        reverse=True,
    ):
        if re.search(
            r"(?<!\w)" + re.escape(phrase) + r"(?!\w)",
            q,
        ):
            return subject

    return None


# ============================================================
# TEACHER EXTRACTION
# ============================================================

def extract_teacher(message: str, timetable=None):
    q = normalize_message(message)

    if not timetable:
        return None

    teachers = set()

    for item in timetable:
        teacher = get_field(item, "teacher_names", "teacher")
        if teacher:
            teachers.add(str(teacher).strip())

    for teacher in sorted(teachers, key=len, reverse=True):
        if normalize_message(teacher) in q:
            return teacher

    return None


# ============================================================
# DATABASE QUERIES
# ============================================================

def get_timetable(
    db: Session,
    course: str | None = None,
    division: str | None = None,
    day: str | None = None,
):
    query = db.query(Timetable)

    if course:
        query = query.filter(
            Timetable.course == normalize_course(course)
        )

    if division:
        query = query.filter(
            Timetable.division == division.upper().strip()
        )

    if day:
        query = query.filter(
            Timetable.day == normalize_day(day)
        )

    return query.order_by(
        Timetable.day.asc(),
        Timetable.start_time.asc(),
    ).all()


def get_timetable_by_class(
    db: Session,
    course: str,
    division: str,
):
    if not course or not division:
        return []

    return get_timetable(
        db,
        course=course,
        division=division,
    )


def get_timetable_by_day(
    db: Session,
    course: str,
    division: str,
    day: str,
):
    if not course or not division or not day:
        return []

    return get_timetable(
        db,
        course=course,
        division=division,
        day=day,
    )


def get_timetable_by_subject(
    db: Session,
    subject: str,
):
    if not subject:
        return []

    normalized = normalize_subject(subject)

    rows = db.query(Timetable).all()

    matches = []

    for item in rows:
        value = get_field(item, "subject_name", "subject_code", "subject")
        if value and normalize_message(value) == normalize_message(normalized):
            matches.append(item)

    return sorted(
        matches,
        key=lambda item: (
            clean_value(get_field(item, "course")) or "",
            clean_value(get_field(item, "division")) or "",
            clean_value(get_field(item, "day")) or "",
            str(get_field(item, "start_time") or ""),
        ),
    )


def get_timetable_by_teacher(
    db: Session,
    teacher: str,
):
    if not teacher:
        return []

    rows = db.query(Timetable).all()

    teacher_q = normalize_message(teacher)

    return [
        item
        for item in rows
        if teacher_q in normalize_message(
            get_field(item, "teacher_names", "teacher") or ""
        )
    ]


def get_subject_schedule(
    db: Session,
    subject: str,
    course: str | None = None,
    division: str | None = None,
):
    rows = get_timetable(
        db,
        course=course,
        division=division,
    )

    normalized = normalize_message(normalize_subject(subject))

    return [
        item
        for item in rows
        if normalize_message(
            get_field(item, "subject_name", "subject_code", "subject") or ""
        ) == normalized
    ]


# ============================================================
# FORMATTERS
# ============================================================

def format_timetable(record: Timetable):
    if not record:
        return None

    return {
        "id": get_field(record, "id"),
        "academic_year": get_field(record, "academic_year"),
        "semester": get_field(record, "semester"),
        "effective_from": get_field(record, "effective_from"),
        "course": get_field(record, "course"),
        "division": get_field(record, "division"),
        "day": get_field(record, "day"),
        "start_time": get_field(record, "start_time"),
        "end_time": get_field(record, "end_time"),
        "subject_code": get_field(record, "subject_code"),
        "subject_name": get_field(record, "subject_name", "subject"),
        "teacher_names": get_field(record, "teacher_names", "teacher"),
        "room": get_field(record, "room"),
        "session_type": get_field(record, "session_type", "lecture_type"),
    }


def format_timetable_list(records):
    if not records:
        return []

    return [format_timetable(record) for record in records]
