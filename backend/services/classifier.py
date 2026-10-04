# ============================================================
# CLASSIFIER.PY
# VSIT STUDENT ASSISTANT
# ============================================================
#
# Purpose:
#   Classify student questions into the correct module.
#
# Categories:
#   RESULT
#   TIMETABLE / VSIT
#   FACULTY
#   OFFICE
#   ACADEMIC
#   CAREER
#   NGO
#   VSIT
#   GENERAL
#
# Important:
#   This file DOES NOT generate answers.
#   It only identifies which module should handle the question.
#
#   Official information must come from:
#       - MySQL structured data
#       - Existing KnowledgeBase
#       - Future RAG system
#
#   Never use this classifier to invent official information.
# ============================================================

import re

from backend.services.query_understanding import normalize_query
from backend.services.local_retrieval import rank_candidates


# ============================================================
# NORMALIZE MESSAGE
# ============================================================

def normalize_message(message):
    """
    Normalize a user message.

    Example:
        "  Who   teaches   IOT? "
        ->
        "who teaches iot?"
    """

    return normalize_query(message)


# ============================================================
# SAFE KEYWORD MATCHING
# ============================================================

def contains_keyword(message, keywords):
    """
    Check whether any keyword exists in the message.

    Uses word boundaries so that:

        "lab"

    does NOT accidentally match:

        "available"

    This prevents the old timetable classification bug.
    """

    if not message:
        return False

    message = normalize_message(message)

    for keyword in keywords:

        if not keyword:
            continue

        keyword = normalize_message(keyword)

        # Exact word / phrase boundary matching
        pattern = (
            r"(?<!\w)"
            + re.escape(keyword)
            + r"(?!\w)"
        )

        if re.search(pattern, message):
            return True

    return False


# ============================================================
# SAFE OFFICIAL INFORMATION RESPONSE
# ============================================================

def official_data_unavailable_response():
    """
    Safe response used when verified VSIT information
    is not available.

    IMPORTANT:
    Never invent official information.
    """

    return (
        "I could not find this information in the available "
        "VSIT data."
    )


# ============================================================
# FACULTY QUESTION DETECTOR
# ============================================================

def is_faculty_question(message: str) -> bool:
    """
    Detect official faculty-related questions.

    Examples:

        Who is the HOD of IT?
        Who is the head of IT department?
        Tell me about faculty members.
        Who teaches IOT?

    NOTE:
    'Who teaches IOT?' is intentionally allowed to continue
    to the timetable/faculty data path because your existing
    chat.py uses timetable records to identify teachers.
    """

    message_lower = normalize_message(message)

    if not message_lower:
        return False

    faculty_patterns = [

        # HOD
        r"\bhod\b",
        r"\bh\.o\.d\b",
        r"\bhead of department\b",
        r"\bhead of the department\b",
        r"\bhead of the [a-z0-9& ]+ department\b",
        r"\bhead of [a-z0-9& ]+ department\b",
        r"\bdepartment head\b",
        r"\bwho is the hod\b",
        r"\bwho is hod\b",
        r"\bwho heads the department\b",
        r"\bwho (?:runs|leads|heads) (?:the )?[a-z0-9& ]+\b",
        r"\bin charge of (?:the )?[a-z0-9& ]+\b",

        # Faculty
        r"\bfaculty\b",
        r"\bfaculty member\b",
        r"\bfaculty members\b",
        r"\bfaculty information\b",
        r"\bfaculty details\b",
        r"\bfaculty list\b",

        # Professors
        r"\bprofessor\b",
        r"\bprofessors\b",
        r"\bassistant professor\b",
        r"\bassociate professor\b",

        # Teaching
        r"\bwho teaches\b",
        r"\bwho teach\b",
        r"\bwhich faculty teaches\b",
        r"\bwhich professor teaches\b",
        r"\bteacher of\b",
        r"\bwho is teaching\b",
    ]

    return any(
        re.search(pattern, message_lower)
        for pattern in faculty_patterns
    )


# ============================================================
# OFFICE QUESTION DETECTOR
# ============================================================

def is_office_question(message: str) -> bool:
    """
    Detect questions related to VSIT offices and
    administrative/student services.

    Examples:

        What are office timings?
        Where is the examination cell?
        Where is the admission office?
        How do I get a bonafide certificate?
        Where is the placement cell?
    """

    message_lower = normalize_message(message)

    if not message_lower:
        return False

    office_patterns = [

        # General office
        r"\boffice\b",
        r"\boffice timing\b",
        r"\boffice timings\b",
        r"\boffice hour\b",
        r"\boffice hours\b",
        r"\bworking hours\b",
        r"\bworking time\b",

        # Examination
        r"\bexamination cell\b",
        r"\bexam cell\b",
        r"\bexamination office\b",
        r"\bexam office\b",

        # Admissions
        r"\badmission office\b",
        r"\badmission cell\b",
        r"\badmission section\b",

        # Accounts
        r"\baccounts office\b",
        r"\baccounts section\b",
        r"\baccount office\b",

        # Student section
        r"\bstudent section\b",
        r"\bstudent office\b",
        r"\bstudent service\b",
        r"\bstudent services\b",

        # Placement
        r"\bplacement cell\b",
        r"\bplacement office\b",
        r"\bplacement section\b",

        # Certificates
        r"\bbonafide\b",
        r"\bbonafide certificate\b",
        r"\bcertificate application\b",
        r"\bcertificate procedure\b",

        # Location
        r"\bwhere is the office\b",
        r"\bwhere is the examination\b",
        r"\bwhere is the exam cell\b",
        r"\bwhere is the admission\b",
        r"\bwhere is the placement\b",
        r"\bwhere is the accounts\b",
        r"\bwhere is the student section\b",

        # Contact
        r"\bwho should i contact for admissions\b",
        r"\bwho should i contact for admission\b",
        r"\bwho should i contact for exams\b",
        r"\bwho should i contact for examination\b",
        r"\bwho should i contact for bonafide\b",
    ]

    return any(
        re.search(pattern, message_lower)
        for pattern in office_patterns
    )


# ============================================================
# ACADEMIC QUESTION DETECTOR
# ============================================================

def is_academic_question(message: str) -> bool:
    """
    Detect academic information questions.

    Examples:

        What is the syllabus for CN?
        When are semester exams?
        Show academic calendar.
        What is the next holiday?
    """

    message_lower = normalize_message(message)

    if not message_lower:
        return False

    academic_patterns = [

        # Academic
        r"\bacademic\b",
        r"\bacademics\b",
        r"\bacademic calendar\b",

        # Examination
        r"\bexam\b",
        r"\bexams\b",
        r"\bexamination\b",
        r"\bexaminations\b",
        r"\bsemester exam\b",
        r"\bsemester exams\b",
        r"\bsemester examination\b",
        r"\bsemester examinations\b",
        r"\bexam schedule\b",
        r"\bexamination schedule\b",

        # Syllabus
        r"\bsyllabus\b",
        r"\bsubject syllabus\b",
        r"\bcourse syllabus\b",

        # Semester
        r"\bsemester\b",
        r"\bsem 1\b",
        r"\bsem 2\b",
        r"\bsem 3\b",
        r"\bsem 4\b",
        r"\bsem 5\b",
        r"\bsem 6\b",

        # Holidays
        r"\bholiday\b",
        r"\bholidays\b",
        r"\bholiday list\b",
        r"\bnext holiday\b",

        # Academic dates
        r"\bsemester dates\b",
        r"\bacademic dates\b",
        r"\bterm dates\b",
        r"\bdeadline\b",
        r"\bdeadlines\b",
        r"\bapplication deadline\b",
        r"\bnotice\b",
        r"\bnotices\b",

        # Internal assessment
        r"\binternal assessment\b",
        r"\binternal assessments\b",
        r"\binternal exam\b",
        r"\binternal exams\b",
        r"\bunit test\b",
        r"\bunit tests\b",

        # Marks / grades
        r"\bmarks\b",
        r"\bgrades\b",
        r"\bgrading\b",
    ]

    return any(
        re.search(pattern, message_lower)
        for pattern in academic_patterns
    )


# ============================================================
# RESULT QUESTION DETECTOR
# ============================================================

def is_result_classifier_question(message: str) -> bool:
    """
    Detect result-related questions.
    """

    message_lower = normalize_message(message)

    if not message_lower:
        return False

    result_patterns = [

        r"\bresult\b",
        r"\bresults\b",

        r"\bsemester result\b",
        r"\bsem result\b",

        r"\bexam result\b",
        r"\bexamination result\b",

        r"\bcheck result\b",
        r"\bcheck my result\b",

        r"\bshow result\b",
        r"\bshow my result\b",

        r"\blatest result\b",

        r"\bresult portal\b",
        r"\bresult page\b",
        r"\bresult website\b",

        r"\bsemester 1 result\b",
        r"\bsemester 2 result\b",
        r"\bsemester 3 result\b",
        r"\bsemester 4 result\b",
        r"\bsemester 5 result\b",
        r"\bsemester 6 result\b",

        r"\bsem 1 result\b",
        r"\bsem 2 result\b",
        r"\bsem 3 result\b",
        r"\bsem 4 result\b",
        r"\bsem 5 result\b",
        r"\bsem 6 result\b",
    ]

    return any(
        re.search(pattern, message_lower)
        for pattern in result_patterns
    )


# ============================================================
# TIMETABLE QUESTION DETECTOR
# ============================================================

def is_timetable_classifier_question(message: str) -> bool:
    """
    Detect timetable/class-related questions.

    IMPORTANT:
    Uses word-boundary matching.

    Therefore:

        "available"

    will NOT trigger:

        "lab"
    """

    message_lower = normalize_message(message)

    if not message_lower:
        return False

    timetable_patterns = [

        # Timetable
        r"\btimetable\b",
        r"\btime table\b",

        # Schedule
        r"\bschedule\b",
        r"\bclass schedule\b",
        r"\bclass timing\b",
        r"\bclass timings\b",

        # Today
        r"\btoday class\b",
        r"\btoday classes\b",
        r"\btoday's class\b",
        r"\btoday's classes\b",

        # Tomorrow
        r"\btomorrow class\b",
        r"\btomorrow classes\b",
        r"\btomorrow's class\b",
        r"\btomorrow's classes\b",

        # Lectures
        r"\blecture\b",
        r"\blectures\b",
        r"\blecture timing\b",
        r"\blecture timings\b",

        # Timings
        r"\bwhen is\b",
        r"\bwhen does\b",
        r"\bwhat time is\b",
        r"\bwhat time does\b",

        # Teachers
        r"\bwho teaches\b",
        r"\bwho teach\b",
        r"\bteacher of\b",
        r"\bwho is teaching\b",

        # Room
        r"\bwhich room\b",
        r"\broom for\b",

        # Practical
        r"\bpractical\b",
        r"\bpracticals\b",

        # Lab
        r"\blab\b",
        r"\blaboratory\b",

        # Period
        r"\bperiod\b",
        r"\bperiods\b",
    ]

    if not any(
        re.search(pattern, message_lower)
        for pattern in timetable_patterns
    ):
        return False

    # --------------------------------------------------------
    # Context words
    # --------------------------------------------------------

    timetable_context = [

        # Courses
        "fyit",
        "syit",
        "tyit",

        # Division
        "division",

        # Timetable terms
        "timetable",
        "schedule",
        "class",
        "classes",
        "lecture",
        "lectures",
        "period",
        "periods",
        "practical",
        "practicals",
        "lab",
        "laboratory",
        "room",

        # Days
        "today",
        "tomorrow",
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",

        # Common subjects
        "iot",
        "iks",
        "ai",
        "mern",
        "jira",
        ".net",
        "dbms",
        "database",
        "computer network",
        "cn",
        "software engineering",
        "os",
        "operating system",
    ]

    return contains_keyword(
        message_lower,
        timetable_context
    )


# ============================================================
# CAREER QUESTION DETECTOR
# ============================================================

def is_career_question(message: str) -> bool:
    """
    Detect career-related questions.
    """

    message_lower = normalize_message(message)

    if not message_lower:
        return False

    career_keywords = [

        "career",
        "career guidance",

        "job",
        "jobs",

        "resume",
        "cv",

        "interview",
        "interviews",

        "developer",
        "software engineer",

        "job preparation",
        "placement preparation",

        "java developer",
        "python developer",
        "software development",

        "career opportunity",
        "career opportunities",

        "internship",
        "internships",

        "placement",
        "placements",
    ]

    return contains_keyword(
        message_lower,
        career_keywords
    )


# ============================================================
# NGO QUESTION DETECTOR
# ============================================================

def is_ngo_question(message: str) -> bool:
    """
    Detect NGO-related questions.
    """

    message_lower = normalize_message(message)

    if not message_lower:
        return False

    ngo_keywords = [

        "ngo",
        "non governmental organization",
        "non-governmental organization",

        "volunteer",
        "volunteering",

        "ngo internship",
        "internship at ngo",

        "ngo program",
        "ngo programs",

        "ngo mission",

        "beneficiary",
        "beneficiaries",

        "donation",
        "donate",
        "donating",

        "social work",
        "community service",

        "ngo activities",
        "ngo services",
    ]

    return contains_keyword(
        message_lower,
        ngo_keywords
    )


# ============================================================
# VSIT / COLLEGE QUESTION DETECTOR
# ============================================================

def is_vsit_question(message: str) -> bool:
    """
    Detect general VSIT/college questions.

    Examples:

        What courses are available at VSIT?
        Tell me about VSIT.
        What facilities are available?
        What departments are there?
    """

    message_lower = normalize_message(message)

    if not message_lower:
        return False

    vsit_keywords = [

        # College name
        "vsit",
        "vidyalankar",
        "vidyalankar school of information technology",

        # About college
        "about vsit",
        "about the college",
        "college information",
        "college details",
        "college profile",

        "what is vsit",
        "what is vidyalankar",

        "tell me about vsit",
        "tell me about vidyalankar",
        "tell me about the college",

        # Vision / Mission
        "vision of vsit",
        "vsit's vision",
        "vsit vision",

        "mission of vsit",
        "vsit's mission",
        "vsit mission",

        "objective of vsit",
        "objectives of vsit",
        "vsit objectives",

        # Admissions
        "admission",
        "admissions",
        "admission process",
        "application process",
        "apply for admission",
        "how to get admission",
        "admission requirements",
        "admission documents",

        # Courses
        "course offered",
        "courses offered",
        "courses at vsit",
        "course at vsit",
        "what courses",
        "what courses are available",
        "which courses are available",

        "program offered",
        "programs offered",
        "program at vsit",
        "programs at vsit",

        "degree offered",
        "degrees offered",
        "b.sc",
        "bsc it",
        "information technology programme",
        "information technology program",
        "computing department",

        # Departments
        "department",
        "departments",
        "department at vsit",
        "departments at vsit",
        "department in vsit",
        "departments in vsit",
        "academic department",

        # Attendance
        "attendance",
        "attendance requirement",
        "minimum attendance",
        "attendance criteria",
        "attendance percentage",
        "attendance policy",
        "how much attendance",

        # Scholarships
        "scholarship",
        "scholarships",
        "financial assistance",
        "financial aid",
        "education funding",

        # Placement
        "placement opportunities",
        "placement assistance",
        "campus placement",
        "job opportunities through college",
        "recruitment",

        # Facilities
        "facility",
        "facilities",
        "college facilities",
        "campus facilities",
        "infrastructure",
        "laboratory",
        "laboratories",
        "computer lab",
        "computer labs",
        "library",
        "library facilities",
        "sports",
        "sports facilities",
        "student clubs",
        "clubs",
        "auditorium",

        # Location
        "college address",
        "college location",
        "vsit address",
        "vsit location",
        "where is vsit",
        "where is the college",

        # Contact
        "college contact",
        "contact details",
        "college phone",
        "college email",
        "college telephone",
        "contact vsit",
        "contact the college",

        # Student support
        "grievance",
        "student complaint",
        "mental health support",
        "medical support",
    ]

    return contains_keyword(
        message_lower,
        vsit_keywords
    )


# ============================================================
# MAIN QUESTION CLASSIFIER
# ============================================================

def classify_question(message):
    """
    Classify a student question.

    Returns one of:

        RESULT
        FACULTY
        OFFICE
        ACADEMIC
        CAREER
        NGO
        VSIT
        GENERAL

    IMPORTANT:
    Timetable-related questions return VSIT because your
    existing chat.py handles timetable questions before
    calling classify_question().
    """

    message = normalize_message(message)

    if not message:
        return "GENERAL"

    if message in {
        "hi", "hello", "hey", "hii", "hiii", "good morning",
        "good afternoon", "good evening", "namaste",
    }:
        return "GREETING"

    # ========================================================
    # 1. RESULT
    # ========================================================

    if is_result_classifier_question(message):
        return "RESULT"

    # ========================================================
    # 2. FACULTY
    # ========================================================
    #
    # HOD / faculty questions must be protected from the
    # generic AI model.
    #
    # BUT:
    # "Who teaches IOT?"
    #
    # is handled by your existing timetable/faculty logic.
    # So don't classify simple teacher-subject questions
    # as FACULTY here.
    # ========================================================

    teacher_subject_question = bool(
        re.search(
            r"\bwho\s+(teaches|teach)\b",
            message
        )
    )

    hod_or_faculty_question = bool(
        re.search(
            r"\bhod\b"
            r"|\bh\.o\.d\b"
            r"|\bhead of department\b"
            r"|\bhead of the department\b"
            r"|\bdepartment head\b"
            r"|\bhead of (?:the )?[a-z0-9& ]+\b",
            message
        )
    )

    if is_faculty_question(message):
        return "FACULTY"

    # ========================================================
    # 3. OFFICE
    # ========================================================
    #
    # IMPORTANT:
    # Office is checked BEFORE general VSIT.
    #
    # Otherwise:
    #
    # "Where is the examination cell?"
    #
    # could become a generic VSIT question.
    # ========================================================

    if is_office_question(message):
        return "OFFICE"

    # ========================================================
    # 4. ACADEMIC
    # ========================================================

    if is_academic_question(message):
        return "ACADEMIC"

    # ========================================================
    # 5. TIMETABLE
    # ========================================================
    #
    # Return VSIT because the existing chat.py already
    # handles timetable questions before classification.
    # ========================================================

    if is_timetable_classifier_question(message):
        return "VSIT"

    # ========================================================
    # 6. NGO
    # ========================================================

    if is_ngo_question(message):
        return "NGO"

    # ========================================================
    # 7. CAREER
    # ========================================================

    if is_career_question(message):
        return "CAREER"

    # ========================================================
    # 8. GENERAL VSIT
    # ========================================================

    if is_vsit_question(message):
        return "VSIT"

    # ========================================================
    # 9. GENERAL
    # ========================================================

    return "GENERAL"


# ============================================================
# KNOWLEDGE BASE SEARCH
# ============================================================

def search_knowledge(user_message, knowledge_list):
    """
    Search existing VSIT/NGO knowledge-base records.

    Expected KnowledgeBase fields:

        topic
        question
        answer

    The function returns the best matching database object
    or None.

    No AI-generated information is produced here.
    """

    if not user_message or not knowledge_list:
        return None

    user_message_lower = normalize_message(
        user_message
    )

    if "coordinat" in user_message_lower and (
        "b.sc" in user_message_lower
        or "bsc" in user_message_lower
    ):
        for item in knowledge_list:
            question = normalize_message(getattr(item, "question", "") or "")
            if "coordinat" in question and ("b.sc" in question or "bsc" in question):
                return item

    # ========================================================
    # KEYWORD GROUPS
    # ========================================================

    keyword_groups = {

        "About College": [
            "what is vsit",
            "what is vidyalankar",
            "tell me about vsit",
            "tell me about vidyalankar",
            "tell me about the college",
            "about vsit",
            "about the college",
            "college information",
            "college details",
            "college profile",
        ],

        "Vision": [
            "vision",
            "vision of vsit",
            "vsit vision",
            "college vision",
        ],

        "Mission": [
            "mission",
            "mission of vsit",
            "vsit mission",
            "college mission",
        ],

        "Objectives": [
            "objective",
            "objectives",
            "main objective",
            "main objectives",
            "objective of vsit",
            "objectives of vsit",
            "vsit objectives",
            "college objectives",
        ],

        "Attendance": [
            "attendance",
            "attendance requirement",
            "minimum attendance",
            "attendance criteria",
            "attendance percentage",
            "attendance policy",
            "how much attendance",
        ],

        "Admissions": [
            "admission",
            "admissions",
            "admission process",
            "application process",
            "apply for admission",
            "how to get admission",
            "admission requirements",
            "admission documents",
        ],

        "Courses": [
            "course",
            "courses",
            "course offered",
            "courses offered",
            "courses at vsit",
            "course at vsit",
            "what courses",
            "what courses are available",
            "which courses are available",
            "program",
            "programs",
            "program offered",
            "programs offered",
            "degree offered",
            "degrees offered",
            "b.sc",
            "bsc it",
            "information technology programme",
            "information technology program",
        ],

        "B.Sc. Information Technology": [
            "b.sc information technology",
            "bsc information technology",
            "information technology programme",
            "information technology program",
        ],

        "Computing department": [
            "computing department",
            "department of computing",
            "computing facilities",
        ],

        "B.Sc. IT coordination": [
            "who coordinates b.sc",
            "b.sc coordinator",
            "bsc coordinator",
        ],

        "Departments": [
            "department",
            "departments",
            "department at vsit",
            "departments at vsit",
            "department in vsit",
            "departments in vsit",
            "academic department",
        ],

        "Scholarships": [
            "scholarship",
            "scholarships",
            "financial assistance",
            "financial aid",
            "education funding",
        ],

        "Placements": [
            "placement",
            "placements",
            "campus placement",
            "placement opportunities",
            "placement assistance",
            "job opportunities through college",
            "recruitment",
        ],

        "Internships": [
            "college internship",
            "internship through college",
            "internship opportunities at vsit",
        ],

        "Contact": [
            "contact",
            "contact details",
            "phone number",
            "telephone",
            "phone",
            "email",
            "email address",
            "address",
            "location",
            "where is vsit",
            "where is the college",
            "college location",
            "vsit location",
            "vsit address",
            "college phone",
            "college email",
        ],

        "Facilities": [
            "facility",
            "facilities",
            "college facilities",
            "campus facilities",
            "infrastructure",
            "laboratory",
            "laboratories",
            "computer lab",
            "computer labs",
            "library",
            "library facilities",
            "sports facilities",
            "sports",
            "student clubs",
            "clubs",
            "auditorium",
        ],

        "Office": [
            "office",
            "office timing",
            "office timings",
            "office hours",
            "examination cell",
            "exam cell",
            "admission cell",
            "accounts office",
            "student section",
            "placement cell",
            "bonafide",
            "bonafide certificate",
        ],

        # NGO topics
        "Volunteer": [
            "volunteer",
            "volunteering",
            "volunteer opportunity",
            "volunteer opportunities",
            "join as a volunteer",
            "help as a volunteer",
        ],

        "Internship": [
            "internship",
            "internships",
            "intern",
        ],

        "Eligibility": [
            "eligible",
            "eligibility",
            "who can apply",
            "qualification",
            "qualifications",
        ],

        "Documents": [
            "document",
            "documents",
            "required documents",
            "proof",
            "certificate",
        ],

        "Donation": [
            "donation",
            "donate",
            "donating",
        ],

        "Programs": [
            "ngo program",
            "ngo programs",
            "ngo activities",
            "ngo services",
        ],
    }

    # ========================================================
    # DETECT USER TOPIC
    # ========================================================

    detected_topic = None

    # Prefer the specific coordination intent over the broader B.Sc. topic.
    if "coordinat" in user_message_lower and (
        "b.sc" in user_message_lower
        or "bsc" in user_message_lower
    ):
        detected_topic = "B.Sc. IT coordination"

    for topic, keywords in keyword_groups.items():
        if detected_topic:
            break

        if contains_keyword(
            user_message_lower,
            keywords
        ):
            detected_topic = topic
            break

    # ========================================================
    # SCORE DATABASE RECORDS
    # ========================================================

    best_match = None
    highest_score = 0

    ignored_words = {
        "what",
        "when",
        "where",
        "which",
        "who",
        "does",
        "the",
        "for",
        "this",
        "that",
        "are",
        "how",
        "can",
        "tell",
        "about",
        "and",
        "you",
        "your",
        "was",
        "with",
        "from",
        "please",
        "tell",
        "me",
    }

    important_words = {
        "vsit",
        "vidyalankar",
        "vision",
        "mission",
        "objective",
        "objectives",
        "attendance",
        "admission",
        "course",
        "courses",
        "department",
        "departments",
        "scholarship",
        "placement",
        "placements",
        "facility",
        "facilities",
        "library",
        "sports",
        "location",
        "address",
        "internship",
        "volunteer",
        "office",
        "certificate",
        "bonafide",
    }

    for item in knowledge_list:

        score = 0

        # ----------------------------------------------------
        # Safely read fields
        # ----------------------------------------------------

        item_topic = normalize_message(
            getattr(item, "topic", "") or ""
        )

        item_question = normalize_message(
            getattr(item, "question", "") or ""
        )

        item_answer = normalize_message(
            getattr(item, "answer", "") or ""
        )

        # ----------------------------------------------------
        # Topic match
        # ----------------------------------------------------

        if detected_topic:

            if item_topic == normalize_message(
                detected_topic
            ):
                score += 60

        # ----------------------------------------------------
        # Topic appears in user question
        # ----------------------------------------------------

        if item_topic:

            if contains_keyword(
                user_message_lower,
                [item_topic]
            ):
                score += 25

        # ----------------------------------------------------
        # Exact question
        # ----------------------------------------------------

        if (
            item_question
            and item_question == user_message_lower
        ):
            score += 100

        # ----------------------------------------------------
        # Question word matching
        # ----------------------------------------------------

        question_words = re.findall(
            r"\b[a-zA-Z]{3,}\b",
            item_question
        )

        for word in question_words:

            if word in ignored_words:
                continue

            if contains_keyword(
                user_message_lower,
                [word]
            ):
                score += 5

        # ----------------------------------------------------
        # Important content matching
        # ----------------------------------------------------

        for word in important_words:

            if not contains_keyword(
                user_message_lower,
                [word]
            ):
                continue

            if (
                contains_keyword(
                    item_question,
                    [word]
                )
                or contains_keyword(
                    item_topic,
                    [word]
                )
                or contains_keyword(
                    item_answer,
                    [word]
                )
            ):
                score += 15

        # ----------------------------------------------------
        # Keep best match
        # ----------------------------------------------------

        if score > highest_score:

            highest_score = score
            best_match = item

    # ========================================================
    # RETURN ONLY STRONG MATCH
    # ========================================================

    if (
        best_match is not None
        and highest_score >= 30
    ):
        return best_match

    ranked = rank_candidates(
        user_message,
        [
            {
                "record": item,
                "category": getattr(item, "category", ""),
                "topic": getattr(item, "topic", ""),
                "question": getattr(item, "question", ""),
                "answer": getattr(item, "answer", ""),
            }
            for item in knowledge_list
        ],
    )
    if ranked:
        return ranked[0]["record"]

    return None
