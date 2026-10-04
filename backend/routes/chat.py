"""
VSIT Student Assistant - Chat Route

This version keeps the existing Office, Faculty, Result, Knowledge and AI
modules, but fixes timetable handling for the CURRENT timetable schema.

Current timetable database fields:
course, division, day, start_time, end_time,
subject_code, subject_name, teacher_names, room, session_type.

The important fix is that the chatbot no longer expects the old fields:
subject, teacher, lecture_type.
"""

import re
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import or_
from sqlalchemy.orm import Session

from backend.database.database import SessionLocal
from backend.models.timetable import Timetable
from backend.models.knowledge import KnowledgeBase
from backend.models.office import Office

from backend.services.classifier import (
    classify_question,
    search_knowledge,
)
from backend.services.query_understanding import normalize_query

from backend.services.ai_service import (
    get_ai_response,
    get_missing_info_response,
)

from backend.services.academic_service import answer_academic_question
from backend.services.document_service import search_documents

from backend.services.result_service import (
    is_result_question,
    search_result,
)

from backend.services.faculty_service import (
    get_faculty_by_subject,
    get_faculty_by_department,
    get_faculty_by_name,
    get_hod,
    get_all_faculty,
)

from backend.services.timetable_service import (
    is_timetable_question,
    extract_timetable_details,
    extract_subject,
    extract_teacher,
    get_timetable_intent,
    detect_relative_day,
    detect_lecture_type,
    normalize_course,
    course_display_name,
    get_timetable,
)


router = APIRouter()


def _private_student_data_response(message: str):
    normalized = normalize_text(message)
    if not re.search(r"\b(my|our|student)\b", normalized):
        return None
    if re.search(r"\b(mark|marks|result|score|grade|attendance|fee|fees|payment|backlog|kt|personal timetable)\b", normalized):
        return make_response(
            message,
            "PRIVATE_DATA",
            "I cannot access private student records from this public assistant. Please use the official student portal or contact the concerned VSIT office; I can guide you to the relevant public page.",
        )
    return None


# ============================================================
# REQUEST MODEL
# ============================================================

class ChatRequest(BaseModel):
    message: str = Field(max_length=4000)
    course: str | None = Field(default=None, max_length=120)
    division: str | None = Field(default=None, pattern=r"^[A-Ea-e]$")


# ============================================================
# DATABASE
# ============================================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ============================================================
# RESPONSE HELPER
# ============================================================

def make_response(
    user_message: str,
    category: str,
    bot_response: str,
    **extra,
):
    response = {
        "user_message": user_message,
        "category": category,
        "bot_response": bot_response,
    }

    response.update(extra)

    return response


def official_data_unavailable_response():
    return (
        "I could not find this information in the available "
        "VSIT data."
    )


# ============================================================
# GENERIC HELPERS
# ============================================================

def value(item, *names):
    for name in names:
        data = getattr(item, name, None)

        if data is not None and str(data).strip():
            return str(data).strip()

    return None


def normalize_text(text):
    return normalize_query(text)


def unique_values(values):
    result = []
    seen = set()

    for item in values:
        if not item:
            continue

        clean = str(item).strip()

        if not clean:
            continue

        key = clean.lower()

        if key not in seen:
            seen.add(key)
            result.append(clean)

    return result


# ============================================================
# FACULTY QUESTION DETECTION
# ============================================================

def is_faculty_question(message: str) -> bool:
    text = normalize_text(message)

    patterns = [
        r"\bhod\b",
        r"\bh\.o\.d\b",
        r"\bhead of department\b",
        r"\bhead of the department\b",
        r"\bdepartment head\b",
        r"\bhead of (?:the )?[a-z0-9& ]+\b",
        r"\bwho (?:runs|leads|heads) (?:the )?[a-z0-9& ]+\b",
        r"\bin charge of (?:the )?[a-z0-9& ]+\b",
        r"\bwho teaches\b",
        r"\bwho teach\b",
        r"\bwho is teaching\b",
        r"\bteacher of\b",
        r"\bwhich faculty teaches\b",
        r"\bwhich professor teaches\b",
        r"\bfaculty\b",
        r"\bfaculty member\b",
        r"\bfaculty members\b",
        r"\bfaculty information\b",
        r"\bfaculty details\b",
        r"\bfaculty list\b",
        r"\bprofessor\b",
        r"\bprofessors\b",
    ]

    return any(
        re.search(pattern, text)
        for pattern in patterns
    )


# ============================================================
# FACULTY SUBJECT EXTRACTION
# ============================================================

def extract_faculty_subject(message: str, db: Session):
    """
    First checks the Faculty table.
    If a subject is not present there, the timetable is checked.

    This is the key fix for questions such as:
      Who teaches .NET?
      Who teaches IKS?
      Who teaches AI?
      Who teaches JIRA?
    """

    text = normalize_text(message)

    # --------------------------------------------------------
    # 1. Faculty table
    # --------------------------------------------------------

    try:
        faculty_records = get_all_faculty(db)
    except Exception:
        faculty_records = []

    candidates = []

    for faculty in faculty_records:
        raw = value(faculty, "subjects")

        if not raw:
            continue

        subjects = re.split(
            r"[,;/|]",
            raw,
        )

        for subject in subjects:
            subject = subject.strip()

            if not subject:
                continue

            if normalize_text(subject) in text:
                candidates.append(
                    (
                        len(normalize_text(subject)),
                        subject,
                    )
                )

    if candidates:
        candidates.sort(
            key=lambda x: x[0],
            reverse=True,
        )

        return candidates[0][1]

    # --------------------------------------------------------
    # 2. Timetable table
    # --------------------------------------------------------

    try:
        rows = db.query(Timetable).all()
    except Exception:
        rows = []

    candidates = []

    for item in rows:
        subject = value(
            item,
            "subject_name",
            "subject_code",
            "subject",
        )

        if not subject:
            continue

        if normalize_text(subject) in text:
            candidates.append(
                (
                    len(normalize_text(subject)),
                    subject,
                )
            )

    if candidates:
        candidates.sort(
            key=lambda x: x[0],
            reverse=True,
        )

        return candidates[0][1]

    # --------------------------------------------------------
    # 3. Common aliases
    # --------------------------------------------------------

    aliases = {
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
        "ira": "IRA",
        "ej": "EJ",
        "ap": "AP",
        "dbms": "DBMS",
        "os": "OS",
        "operating system": "OS",
        "cn": "CN",
        "computer networks": "CN",
    }

    for phrase, subject in sorted(
        aliases.items(),
        key=lambda x: len(x[0]),
        reverse=True,
    ):
        if re.search(
            r"(?<!\w)" + re.escape(phrase) + r"(?!\w)",
            text,
        ):
            return subject

    return None


# ============================================================
# DEPARTMENT EXTRACTION
# ============================================================

def extract_faculty_department(message: str, db: Session):
    text = normalize_text(message)

    try:
        records = get_all_faculty(db)
    except Exception:
        records = []

    departments = []

    for faculty in records:
        department = value(
            faculty,
            "department",
        )

        if department:
            departments.append(
                department
            )

    departments = unique_values(
        departments
    )

    candidates = []

    for department in departments:
        dep_text = normalize_text(
            department
        )

        if dep_text in text:
            candidates.append(
                (
                    len(dep_text),
                    department,
                )
            )

    if candidates:
        candidates.sort(
            key=lambda x: x[0],
            reverse=True,
        )

        return candidates[0][1]

    # Common shorthand.
    if re.search(r"\bit\b", text):
        return "Information Technology"

    if re.search(r"\bcs\b", text):
        return "Computer Science"

    return None


# ============================================================
# TIMETABLE TEACHER FALLBACK
# ============================================================

def find_teacher_from_timetable(
    message: str,
    db: Session,
):
    """
    Search the timetable directly for:
        Who teaches IOT?
        Who teaches .NET?
        Who teaches IKS?
        Who teaches AI?
        etc.

    This is deliberately independent of the Faculty table.
    """

    subject = extract_faculty_subject(
        message,
        db,
    )

    if not subject:
        return None, None

    try:
        rows = db.query(Timetable).all()
    except Exception:
        return subject, []

    subject_q = normalize_text(subject)

    matching = []

    for row in rows:
        row_subjects = unique_values(
            [
                value(row, "subject_name", "subject"),
                value(row, "subject_code"),
            ]
        )
        normalized_subjects = [normalize_text(item) for item in row_subjects]

        if any(
            row_subject == subject_q or subject_q in row_subject
            for row_subject in normalized_subjects
        ):
            matching.append(row)

    teachers = []

    for row in matching:
        teacher = value(
            row,
            "teacher_names",
            "teacher",
        )

        if teacher:
            teachers.append(
                teacher
            )

    teachers = unique_values(
        teachers
    )

    return subject, teachers


# ============================================================
# FACULTY HANDLER
# ============================================================

def handle_faculty_question(
    message: str,
    db: Session,
):
    text = normalize_text(message)

    # ========================================================
    # HOD
    # ========================================================

    if (
        re.search(r"\bhod\b", text)
        or re.search(r"\bh\.o\.d\b", text)
        or "head of department" in text
        or "head of the department" in text
        or "department head" in text
        or re.search(r"\bhead of (?:the )?.*department\b", text)
        or re.search(r"\bhead of (?:the )?[a-z0-9& ]+\b", text)
        or re.search(r"\bwho (?:runs|leads|heads) (?:the )?[a-z0-9& ]+\b", text)
        or re.search(r"\bin charge of (?:the )?[a-z0-9& ]+\b", text)
    ):
        department = extract_faculty_department(
            message,
            db,
        )

        if department:
            try:
                faculty = get_hod(
                    db,
                    department,
                )
            except Exception:
                faculty = None

            if faculty:
                response = (
                    f"👨‍🏫 {value(faculty, 'name')} "
                    f"is the HOD of the "
                    f"{value(faculty, 'department') or department} "
                    f"department."
                )

                designation = value(
                    faculty,
                    "designation",
                )

                if designation:
                    response += (
                        f"\n💼 Designation: "
                        f"{designation}"
                    )

                email = value(
                    faculty,
                    "email",
                )

                if email:
                    response += (
                        f"\n📧 Email: {email}"
                    )

                phone = value(
                    faculty,
                    "phone",
                )

                if phone:
                    response += (
                        f"\n📞 Phone: {phone}"
                    )

                return make_response(
                    message,
                    "FACULTY",
                    response,
                )

        return make_response(
            message,
            "FACULTY",
            "I could not find the HOD information in the available VSIT data.",
        )

    # ========================================================
    # WHO TEACHES SUBJECT
    # ========================================================

    teacher_question = (
        "who teaches" in text
        or "who teach" in text
        or "who is teaching" in text
        or "teacher of" in text
        or "which faculty teaches" in text
        or "which professor teaches" in text
    )

    if teacher_question:
        subject = extract_faculty_subject(
            message,
            db,
        )

        if not subject:
            return make_response(
                message,
                "FACULTY",
                (
                    "Please specify the subject. "
                    "For example: Who teaches IOT?"
                ),
            )

        # ----------------------------------------------------
        # First try Faculty table.
        # ----------------------------------------------------

        try:
            faculty_list = get_faculty_by_subject(
                db,
                subject,
            )
        except Exception:
            faculty_list = []

        if faculty_list:
            responses = []
            seen = set()

            for faculty in faculty_list:
                name = value(
                    faculty,
                    "name",
                )

                if not name:
                    continue

                if name.lower() in seen:
                    continue

                seen.add(name.lower())

                line = (
                    f"👨‍🏫 {name} teaches "
                    f"{subject}."
                )

                department = value(
                    faculty,
                    "department",
                )

                if department:
                    line += (
                        f"\n🏢 Department: "
                        f"{department}"
                    )

                designation = value(
                    faculty,
                    "designation",
                )

                if designation:
                    line += (
                        f"\n💼 Designation: "
                        f"{designation}"
                    )

                responses.append(
                    line
                )

            if responses:
                return make_response(
                    message,
                    "FACULTY",
                    "\n\n".join(
                        responses
                    ),
                )

        # ----------------------------------------------------
        # Faculty table does not contain this subject.
        # Search timetable.
        # ----------------------------------------------------

        timetable_subject, teachers = (
            find_teacher_from_timetable(
                message,
                db,
            )
        )

        if teachers:
            return make_response(
                message,
                "FACULTY",
                (
                    f"👨‍🏫 "
                    f"{', '.join(teachers)} "
                    f"teaches "
                    f"{timetable_subject}."
                ),
            )

        return make_response(
            message,
            "FACULTY",
            (
                f"I could not find faculty information "
                f"for {subject} in the available VSIT data."
            ),
        )

    # ========================================================
    # FACULTY NAME SEARCH
    # ========================================================

    try:
        faculty_records = get_all_faculty(
            db
        )
    except Exception:
        faculty_records = []

    for faculty in faculty_records:
        name = value(
            faculty,
            "name",
        )

        if not name:
            continue

        if normalize_text(name) in text:
            response = (
                f"👨‍🏫 {name}"
            )

            department = value(
                faculty,
                "department",
            )

            if department:
                response += (
                    f"\n🏢 Department: "
                    f"{department}"
                )

            designation = value(
                faculty,
                "designation",
            )

            if designation:
                response += (
                    f"\n💼 Designation: "
                    f"{designation}"
                )

            subjects = value(
                faculty,
                "subjects",
            )

            if subjects:
                response += (
                    f"\n📚 Subjects: "
                    f"{subjects}"
                )

            return make_response(
                message,
                "FACULTY",
                response,
            )

    # ========================================================
    # GENERAL FACULTY
    # ========================================================

    if faculty_records:
        lines = [
            "👨‍🏫 Faculty information available in VSIT:",
            "",
        ]

        for faculty in faculty_records:
            name = value(
                faculty,
                "name",
            )

            if not name:
                continue

            line = f"• {name}"

            department = value(
                faculty,
                "department",
            )

            if department:
                line += (
                    f" — {department}"
                )

            designation = value(
                faculty,
                "designation",
            )

            if designation:
                line += (
                    f" — {designation}"
                )

            lines.append(line)

        if len(lines) > 2:
            return make_response(
                message,
                "FACULTY",
                "\n".join(lines),
            )

    return make_response(
        message,
        "FACULTY",
        official_data_unavailable_response(),
    )


# ============================================================
# OFFICE MODULE
# ============================================================

OFFICE_ALIASES = {
    "Admission Office": [
        "admission",
        "admissions",
        "admission office",
        "admissions office",
        "admission cell",
        "admissions cell",
    ],
    "Placement Cell": [
        "placement",
        "placements",
        "placement cell",
        "placement office",
        "training and placement",
        "training placement",
    ],
    "Accounts Office": [
        "account",
        "accounts",
        "account office",
        "accounts office",
        "account section",
        "accounts section",
        "fees",
        "fee office",
        "fee section",
        "finance office",
        "finance section",
    ],
    "Examination Cell": [
        "exam",
        "exams",
        "examination",
        "examinations",
        "exam cell",
        "examination cell",
        "exam office",
        "examination office",
        "examination section",
    ],
    "Student Section": [
        "student section",
        "student office",
        "student services",
        "student service",
        "student affairs",
        "bonafide",
        "bonafide certificate",
        "bonafide certificate application",
    ],
}


def normalize_office_text(value_text):
    if not value_text:
        return ""

    text = str(value_text).lower().strip()

    text = re.sub(
        r"[^a-z0-9]+",
        " ",
        text,
    )

    return re.sub(
        r"\s+",
        " ",
        text,
    ).strip()


def get_office_alias(message):
    text = normalize_office_text(
        message
    )

    candidates = []

    for office_name, aliases in OFFICE_ALIASES.items():
        for alias in aliases:
            alias_text = normalize_office_text(
                alias
            )

            if re.search(
                r"\b"
                + re.escape(alias_text)
                + r"\b",
                text,
            ):
                candidates.append(
                    (
                        len(alias_text),
                        office_name,
                    )
                )

    if not candidates:
        return None

    candidates.sort(
        key=lambda x: x[0],
        reverse=True,
    )

    return candidates[0][1]


def get_office_intent(message):
    text = normalize_office_text(
        message
    )

    if any(
        term in text
        for term in [
            "timing",
            "timings",
            "office hours",
            "working hours",
            "working time",
            "hours",
            "when is the office open",
            "when does the office open",
            "when does the office close",
        ]
    ):
        return "timing"

    if any(
        term in text
        for term in [
            "contact",
            "phone",
            "mobile",
            "telephone",
            "email",
            "call",
            "whom should i contact",
            "who should i contact",
        ]
    ):
        return "contact"

    if any(
        term in text
        for term in [
            "procedure",
            "process",
            "how do i",
            "how can i",
            "how to",
            "apply",
            "application",
            "steps",
            "requirements",
            "bonafide",
            "certificate",
        ]
    ):
        return "procedure"

    if any(
        term in text
        for term in [
            "where",
            "location",
            "located",
            "room",
            "address",
            "where can i find",
        ]
    ):
        return "location"

    if any(
        term in text
        for term in [
            "what does",
            "what do",
            "purpose",
            "handles",
            "handle",
            "responsible for",
            "information about",
            "details about",
        ]
    ):
        return "purpose"

    return "general"


def get_office_record(
    db: Session,
    office_name,
):
    if not office_name:
        return None

    try:
        records = (
            db.query(Office)
            .filter(
                Office.is_active.is_(True)
            )
            .all()
        )
    except Exception:
        return None

    target = normalize_office_text(
        office_name
    )

    for record in records:
        stored = normalize_office_text(
            value(
                record,
                "office_name",
            )
        )

        if stored == target:
            return record

    return None


def is_office_question(message):
    text = normalize_office_text(
        message
    )

    patterns = [
        r"\boffice\b",
        r"\boffice timing",
        r"\boffice timings",
        r"\boffice hours",
        r"\bworking hours\b",
        r"\badmission\b",
        r"\badmissions\b",
        r"\bplacement\b",
        r"\bplacements\b",
        r"\baccount\b",
        r"\baccounts\b",
        r"\bfees\b",
        r"\bfee office\b",
        r"\bexam(?:ination)?\s+(?:cell|office|section)\b",
        r"\b(?:contact|office|cell)\b.*\b(?:exam|exams|examination|examinations)\b",
        r"\bstudent section\b",
        r"\bstudent services\b",
        r"\bbonafide\b",
        r"\bcertificate application\b",
    ]

    return any(
        re.search(
            pattern,
            text,
        )
        for pattern in patterns
    )


def format_office_record(
    record,
    message,
):
    office_name = value(
        record,
        "office_name",
    ) or "VSIT Office"

    department = value(
        record,
        "department",
    )

    timings = value(
        record,
        "timings",
    )

    location = value(
        record,
        "location",
    )

    purpose = value(
        record,
        "purpose",
    )

    procedure_details = value(
        record,
        "procedure_details",
    )

    contact_person = value(
        record,
        "contact_person",
    )

    contact_email = value(
        record,
        "contact_email",
    )

    contact_phone = value(
        record,
        "contact_phone",
    )

    intent = get_office_intent(
        message
    )

    lines = [
        f"🏢 {office_name}"
    ]

    if department:
        lines.append(
            f"📂 Category: {department}"
        )

    if intent == "timing":
        lines.append(
            "🕒 Office Hours: "
            + timings
            if timings
            else
            "🕒 Office timing is not available in the current VSIT data."
        )

    elif intent == "location":
        lines.append(
            "📍 Location: "
            + location
            if location
            else
            "📍 Location is not available in the current VSIT data."
        )

    elif intent == "procedure":
        lines.append(
            "📋 Procedure: "
            + procedure_details
            if procedure_details
            else
            "📋 Procedure information is not available in the current VSIT data."
        )

    elif intent == "contact":
        found = False

        if contact_person:
            lines.append(
                f"👤 Contact Person: {contact_person}"
            )
            found = True

        if contact_email:
            lines.append(
                f"📧 Email: {contact_email}"
            )
            found = True

        if contact_phone:
            lines.append(
                f"📞 Phone: {contact_phone}"
            )
            found = True

        if not found:
            lines.append(
                "📞 Contact information is not available in the current VSIT data."
            )

    elif intent == "purpose":
        lines.append(
            "ℹ️ "
            + purpose
            if purpose
            else
            "ℹ️ Purpose information is not available in the current VSIT data."
        )

    else:
        found = False

        if purpose:
            lines.append(
                f"ℹ️ {purpose}"
            )
            found = True

        if timings:
            lines.append(
                f"🕒 Office Hours: {timings}"
            )
            found = True

        if location:
            lines.append(
                f"📍 Location: {location}"
            )
            found = True

        if procedure_details:
            lines.append(
                f"📋 Procedure: {procedure_details}"
            )
            found = True

        if not found:
            lines.append(
                "No additional official information is available in the current VSIT data."
            )

    return "\n".join(lines)


def handle_office_question(
    message,
    db,
):
    office_name = get_office_alias(
        message
    )

    if office_name:
        record = get_office_record(
            db,
            office_name,
        )

        if not record:
            return make_response(
                message,
                "OFFICE",
                (
                    "I could not find official "
                    f"information for the "
                    f"{office_name} in the available "
                    "VSIT data."
                ),
            )

        return make_response(
            message,
            "OFFICE",
            format_office_record(
                record,
                message,
            ),
        )

    # A generic office question should use the verified main contact record.
    # Keep unknown named offices on the explicit unavailable-data path above.
    record = (
        db.query(Office)
        .filter(Office.is_active.is_(True))
        .order_by(Office.id)
        .first()
    )
    if record:
        return make_response(
            message,
            "OFFICE",
            format_office_record(record, message),
        )

    return make_response(
        message,
        "OFFICE",
        official_data_unavailable_response(),
    )


# ============================================================
# TIMETABLE FORMATTER
# ============================================================

def format_time_table(
    items,
    title,
):
    lines = [
        f"📅 {title}",
        "",
    ]

    for item in items:
        start_time = value(
            item,
            "start_time",
        ) or "-"

        end_time = value(
            item,
            "end_time",
        ) or "-"

        subject = value(
            item,
            "subject_name",
            "subject_code",
            "subject",
        ) or "-"

        subject_code = value(
            item,
            "subject_code",
        )

        teacher = value(
            item,
            "teacher_names",
            "teacher",
        ) or "-"

        room = value(
            item,
            "room",
        ) or "-"

        session_type = value(
            item,
            "session_type",
            "lecture_type",
        ) or "-"

        subject_line = (
            f"📚 Subject: {subject}"
        )

        if subject_code and (
            normalize_text(subject_code)
            != normalize_text(subject)
        ):
            subject_line += (
                f" ({subject_code})"
            )

        lines.extend(
            [
                f"🕒 {start_time} - {end_time}",
                subject_line,
                f"👨‍🏫 Teacher: {teacher}",
                f"🏫 Room: {room}",
                f"📝 Type: {session_type}",
                "",
            ]
        )

    return "\n".join(lines).strip()


# ============================================================
# NON-TIMETABLE PROTECTION
# ============================================================

def is_obviously_non_timetable_question(
    message,
):
    text = normalize_text(message)

    patterns = [
        r"\bwhat courses\b",
        r"\bwhich courses\b",
        r"\bcourses available\b",
        r"\bavailable courses\b",
        r"\bdegree programs\b",
        r"\bprograms available\b",
        r"\badmission office\b",
        r"\badmission cell\b",
        r"\baccounts office\b",
        r"\bplacement cell\b",
        r"\bstudent section\b",
        r"\bexamination cell\b",
        r"\bbonafide\b",
        r"\bcertificate\b",
        r"\bsports facilities\b",
        r"\bstudent clubs\b",
        r"\blibrary facilities\b",
        r"\bauditorium\b",
        r"\bwho is the hod\b",
        r"\bwho is hod\b",
        r"\bhead of department\b",
        r"\bacademic calendar\b",
        r"\bexam(?:s|ination|inations)?\b",
        r"\bsemester exams\b",
        r"\bexam schedule\b",
        r"\bholiday list\b",
        r"\bsyllabus\b",
    ]

    return any(
        re.search(
            pattern,
            text,
        )
        for pattern in patterns
    )


# ============================================================
# TIMETABLE ROUTE HANDLER
# ============================================================

def handle_timetable_question(
    user_message,
    db,
):
    details = extract_timetable_details(
        user_message
    )

    course = details.get(
        "course"
    )

    division = details.get(
        "division"
    )

    day = details.get(
        "day"
    )

    relative_day = detect_relative_day(
        user_message
    )

    if relative_day:
        day = relative_day

    lecture_type = detect_lecture_type(
        user_message
    )

    # Current database contains B.Sc. Information Technology.
    if not course:
        course = "TYIT"

    course = normalize_course(
        course
    )

    display_course = course_display_name(
        course
    )

    if division:
        division = division.upper().strip()

    intent = get_timetable_intent(
        user_message
    )

    # ========================================================
    # TEACHER QUESTION WITHOUT DIVISION
    # ========================================================

    if intent == "TEACHER" and not division:
        subject = extract_subject(
            user_message
        )

        if not subject:
            try:
                all_rows = db.query(
                    Timetable
                ).all()
            except Exception:
                all_rows = []

            subject = extract_subject(
                user_message,
                all_rows,
            )

        if not subject:
            return make_response(
                user_message,
                "TIMETABLE",
                (
                    "Please specify the subject. "
                    "For example: Who teaches IOT?"
                ),
            )

        rows = get_timetable(
            db,
            course=course,
        )

        matching = []

        subject_q = normalize_text(
            subject
        )

        for item in rows:
            row_subject = value(
                item,
                "subject_name",
                "subject_code",
                "subject",
            )

            if not row_subject:
                continue

            row_q = normalize_text(
                row_subject
            )

            if (
                row_q == subject_q
                or row_q == normalize_text(
                    str(subject)
                )
            ):
                matching.append(item)

        teachers = unique_values(
            [
                value(
                    item,
                    "teacher_names",
                    "teacher",
                )
                for item in matching
            ]
        )

        if not teachers:
            return make_response(
                user_message,
                "TIMETABLE",
                (
                    f"I could not find teacher "
                    f"information for {subject} "
                    f"in the available timetable."
                ),
            )

        divisions = unique_values(
            [
                value(item, "division")
                for item in matching
            ]
        )

        division_text = (
            ", ".join(
                [d.upper() for d in divisions]
            )
            if divisions
            else "the available divisions"
        )

        return make_response(
            user_message,
            "TIMETABLE",
            (
                f"👨‍🏫 {', '.join(teachers)} "
                f"teaches {subject} for "
                f"{display_course} "
                f"Division(s) {division_text}."
            ),
        )

    # ========================================================
    # ALL OTHER TIMETABLE QUESTIONS REQUIRE DIVISION
    # ========================================================

    if not division:
        return make_response(
            user_message,
            "TIMETABLE",
            (
                "Please specify your division. "
                "For example: What is the timetable "
                "for TYIT Division A on Monday?"
            ),
        )

    # ========================================================
    # BASE TIMETABLE
    # ========================================================

    base_timetable = get_timetable(
        db,
        course=course,
        division=division,
    )

    if not base_timetable:
        return make_response(
            user_message,
            "TIMETABLE",
            (
                f"I could not find timetable "
                f"information for {display_course} "
                f"Division {division}."
            ),
        )

    # ========================================================
    # DAY FILTER
    # ========================================================

    if day:
        timetable = [
            item
            for item in base_timetable
            if normalize_text(
                value(item, "day")
            )
            == normalize_text(day)
        ]
    else:
        timetable = list(
            base_timetable
        )

    # ========================================================
    # THEORY / PRACTICAL FILTER
    # ========================================================

    if lecture_type:
        filtered = [
            item
            for item in timetable
            if normalize_text(
                value(
                    item,
                    "session_type",
                    "lecture_type",
                )
            )
            == normalize_text(
                lecture_type
            )
        ]

        timetable = filtered

    # ========================================================
    # SUBJECT / TEACHER
    # ========================================================

    search_items = (
        timetable
        if timetable
        else base_timetable
    )

    subject = extract_subject(
        user_message,
        search_items,
    )

    teacher = extract_teacher(
        user_message,
        search_items,
    )

    # ========================================================
    # FULL TIMETABLE
    # ========================================================

    if intent == "FULL_TIMETABLE":
        if not day:
            return make_response(
                user_message,
                "TIMETABLE",
                (
                    "Please specify the day for the "
                    "timetable. For example: Monday, "
                    "Tuesday, or tomorrow."
                ),
            )

        if not timetable:
            type_text = (
                f" {lecture_type.lower()}"
                if lecture_type
                else ""
            )

            return make_response(
                user_message,
                "TIMETABLE",
                (
                    f"📅 {display_course} Division "
                    f"{division} has no{type_text} "
                    f"classes scheduled on {day}."
                ),
            )

        title = (
            f"Timetable for {display_course} "
            f"Division {division} — {day}"
        )

        if lecture_type:
            title += (
                f" ({lecture_type})"
            )

        return make_response(
            user_message,
            "TIMETABLE",
            format_time_table(
                timetable,
                title,
            ),
        )

    # ========================================================
    # WHO TEACHES SUBJECT
    # ========================================================

    if intent == "TEACHER":
        if not subject:
            return make_response(
                user_message,
                "TIMETABLE",
                (
                    "Please specify the subject. "
                    "For example: Who teaches IOT "
                    "in TYIT A?"
                ),
            )

        matching = [
            item
            for item in timetable
            if normalize_text(
                value(
                    item,
                    "subject_name",
                    "subject_code",
                    "subject",
                )
            )
            == normalize_text(subject)
        ]

        teachers = unique_values(
            [
                value(
                    item,
                    "teacher_names",
                    "teacher",
                )
                for item in matching
            ]
        )

        if not teachers:
            return make_response(
                user_message,
                "TIMETABLE",
                (
                    f"No teacher information is "
                    f"available for {subject}."
                ),
            )

        response = (
            f"👨‍🏫 {', '.join(teachers)} teaches "
            f"{subject} for {display_course} "
            f"Division {division}"
        )

        if day:
            response += (
                f" on {day}"
            )

        response += "."

        return make_response(
            user_message,
            "TIMETABLE",
            response,
        )

    # ========================================================
    # TEACHER -> SUBJECTS
    # ========================================================

    if intent == "TEACHER_SUBJECT":
        if not teacher:
            return make_response(
                user_message,
                "TIMETABLE",
                (
                    "Please specify the teacher's "
                    "name. For example: What subjects "
                    "does Swarupa G. teach in TYIT A?"
                ),
            )

        matching = [
            item
            for item in timetable
            if normalize_text(
                value(
                    item,
                    "teacher_names",
                    "teacher",
                )
            )
            == normalize_text(teacher)
        ]

        subjects = unique_values(
            [
                value(
                    item,
                    "subject_name",
                    "subject_code",
                    "subject",
                )
                for item in matching
            ]
        )

        if not subjects:
            return make_response(
                user_message,
                "TIMETABLE",
                (
                    f"I could not find any classes "
                    f"taught by {teacher} for "
                    f"{display_course} Division "
                    f"{division}."
                ),
            )

        if len(subjects) == 1:
            response = (
                f"📚 {teacher} teaches "
                f"{subjects[0]} for "
                f"{display_course} Division "
                f"{division}"
            )
        else:
            response = (
                f"📚 {teacher} teaches the following "
                f"subjects for {display_course} "
                f"Division {division}:\n\n"
                + "\n".join(
                    f"• {subject_name}"
                    for subject_name in subjects
                )
            )

        if day:
            response += (
                f" on {day}"
            )

        response += "."

        return make_response(
            user_message,
            "TIMETABLE",
            response,
        )

    # ========================================================
    # ROOM / LAB
    # ========================================================

    if intent == "ROOM":
        if not subject:
            return make_response(
                user_message,
                "TIMETABLE",
                (
                    "Please specify the subject. "
                    "For example: Where is the IOT "
                    "lab for TYIT A?"
                ),
            )

        matching = [
            item
            for item in timetable
            if normalize_text(
                value(
                    item,
                    "subject_name",
                    "subject_code",
                    "subject",
                )
            )
            == normalize_text(subject)
        ]

        rooms = unique_values(
            [
                value(item, "room")
                for item in matching
            ]
        )

        if not rooms:
            return make_response(
                user_message,
                "TIMETABLE",
                (
                    f"No room information is "
                    f"available for {subject}."
                ),
            )

        return make_response(
            user_message,
            "TIMETABLE",
            (
                f"🏫 {subject} for "
                f"{display_course} Division "
                f"{division} is scheduled in "
                f"room(s): {', '.join(rooms)}."
            ),
        )

    # ========================================================
    # SUBJECT TIME
    # ========================================================

    if intent == "SUBJECT_TIME":
        if not subject:
            return make_response(
                user_message,
                "TIMETABLE",
                (
                    "Please specify the subject. "
                    "For example: When is the IOT "
                    "lecture for TYIT A?"
                ),
            )

        matching = [
            item
            for item in timetable
            if normalize_text(
                value(
                    item,
                    "subject_name",
                    "subject_code",
                    "subject",
                )
            )
            == normalize_text(subject)
        ]

        if not matching:
            return make_response(
                user_message,
                "TIMETABLE",
                (
                    f"📚 No {subject} class was "
                    f"found for {display_course} "
                    f"Division {division}"
                    + (
                        f" on {day}."
                        if day
                        else "."
                    )
                ),
            )

        lines = [
            f"🕒 {subject} schedule for "
            f"{display_course} Division {division}:",
            "",
        ]

        for item in matching:
            lines.extend(
                [
                    f"📅 {value(item, 'day') or '-'}",
                    (
                        f"🕒 {value(item, 'start_time') or '-'}"
                        f" - "
                        f"{value(item, 'end_time') or '-'}"
                    ),
                    (
                        f"👨‍🏫 Teacher: "
                        f"{value(item, 'teacher_names', 'teacher') or '-'}"
                    ),
                    (
                        f"🏫 Room: "
                        f"{value(item, 'room') or '-'}"
                    ),
                    (
                        f"📝 Type: "
                        f"{value(item, 'session_type', 'lecture_type') or '-'}"
                    ),
                    "",
                ]
            )

        return make_response(
            user_message,
            "TIMETABLE",
            "\n".join(lines).strip(),
        )

    # ========================================================
    # FALLBACK
    # ========================================================

    return make_response(
        user_message,
        "TIMETABLE",
        (
            "I understand that you are asking about "
            "the timetable. Please mention the course, "
            "division and day. For example: "
            "'What is the timetable for TYIT A on Monday?'"
        ),
    )


# ============================================================
# CHAT ROUTE
# ============================================================

@router.post("/chat")
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    user_message = (
        request.message or ""
    ).strip()

    # Allow the UI to persist a student's selected course/division without
    # exposing private records or requiring an account.
    if request.course:
        user_message = f"{user_message} {request.course}"
    if request.division:
        user_message = f"{user_message} division {request.division}"

    # ========================================================
    # EMPTY MESSAGE
    # ========================================================

    if not user_message:
        return make_response(
            "",
            "GENERAL",
            "Please enter a question.",
        )

    private_response = _private_student_data_response(user_message)
    if private_response:
        return private_response

    # ========================================================
    # 1. OFFICE
    # ========================================================

    if is_office_question(
        user_message
    ):
        return handle_office_question(
            user_message,
            db,
        )

    # ========================================================
    # 2. FACULTY
    # ========================================================

    if is_faculty_question(
        user_message
    ):
        return handle_faculty_question(
            user_message,
            db,
        )

    # ========================================================
    # 3. TIMETABLE
    # ========================================================

    timetable_question = False

    if not is_obviously_non_timetable_question(
        user_message
    ):
        try:
            timetable_question = (
                is_timetable_question(
                    user_message
                )
            )
        except Exception:
            timetable_question = False

    if timetable_question:
        return handle_timetable_question(
            user_message,
            db,
        )

    # ========================================================
    # 4. CLASSIFIER
    # ========================================================

    category = classify_question(
        user_message
    )

    if category == "GREETING":
        return make_response(
            user_message,
            category,
            "Hello! I can help with VSIT faculty, offices, timetables, "
            "exams, results and college information. What would you like "
            "to know?",
        )

    # ========================================================
    # 5. RESULT
    # ========================================================

    if (
        category == "RESULT"
        or is_result_question(
            user_message
        )
    ):
        result = search_result(
            db,
            user_message,
        )

        if result:
            return make_response(
                user_message,
                "RESULT",
                f"🎓 {result.title}",
                result_url=result.url,
            )

        return make_response(
            user_message,
            "RESULT",
            "I couldn't find that result.",
            result_url=(
                "https://vsit.edu.in/result/"
            ),
        )

    # ========================================================
    # 6. VERIFIED ACADEMIC EVENTS
    # ========================================================

    if category == "ACADEMIC":
        academic_answer = answer_academic_question(db, user_message)

        if academic_answer:
            return make_response(
                user_message,
                category,
                academic_answer.pop("bot_response"),
                **academic_answer,
            )

    # ========================================================
    # 7. VERIFIED KNOWLEDGE BASE
    # ========================================================

    if category in [
        "VSIT", "NGO", "ADMISSIONS", "PLACEMENTS", "LIBRARY",
        "STUDENT_SUPPORT", "STUDENT_LIFE", "CAMPUS",
        "RESULT", "ACADEMIC", "CAREER",
    ]:
        categories = [category]
        if category in {"VSIT", "CAREER"}:
            categories.extend(["FACULTY", "ADMISSIONS", "PLACEMENTS", "LIBRARY", "ACADEMIC", "STUDENT_SUPPORT", "STUDENT_LIFE", "CAMPUS"])
        if category == "ACADEMIC":
            categories.extend(["ACADEMIC", "RESULT"])
        knowledge_list = (
            db.query(KnowledgeBase)
            .filter(KnowledgeBase.category.in_(categories))
            .all()
        )

        best_match = search_knowledge(
            user_message,
            knowledge_list,
        )

        if best_match:
            return make_response(
                user_message,
                category,
                best_match.answer,
            )

    # ========================================================
    # 8. COLLEGE DOCUMENTS
    # ========================================================

    document_hits = search_documents(db, user_message)

    if document_hits:
        best_hit = document_hits[0]
        return make_response(
            user_message,
            "DOCUMENT",
            best_hit.excerpt,
            sources=[
                {
                    "document_id": hit.document_id,
                    "title": hit.title,
                    "page": hit.page,
                    "score": hit.score,
                }
                for hit in document_hits
            ],
        )

    if category == "ACADEMIC":
        return make_response(
            user_message,
            category,
            (
                "I could not find a verified academic date or notice in the "
                "available VSIT data. Please check an official VSIT notice or "
                "contact the concerned department."
            ),
        )

    if category in ["VSIT", "NGO"]:
        return make_response(
            user_message,
            category,
            get_missing_info_response(
                user_message=user_message,
                category=category,
            ),
        )

    # ========================================================
    # 9. FACULTY FALLBACK
    # ========================================================

    if category == "FACULTY":
        return handle_faculty_question(
            user_message,
            db,
        )

    # 10. CAREER
    # ========================================================

    if category == "CAREER":
        response = get_ai_response(
            user_message,
            category,
        )

        return make_response(
            user_message,
            category,
            response,
        )

    # ========================================================
    # 11. GENERAL
    # ========================================================

    response = get_ai_response(
        user_message,
        "GENERAL",
    )

    return make_response(
        user_message,
        category,
        response,
    )
