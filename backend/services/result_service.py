import re

from backend.models.result import Result


# ------------------------------------------------------
# Detect if question is about result
# ------------------------------------------------------

def is_result_question(message):

    message = message.lower()

    keywords = [

        "result",
        "results",

        "semester result",
        "sem result",

        "exam result",

        "check result",

        "show result",

        "latest result",

        "result portal"
    ]

    return any(word in message for word in keywords)


# ------------------------------------------------------
# Extract Semester
# ------------------------------------------------------

def extract_semester(message):

    message = message.lower()

    semester_map = {

        "sem 1": "1",
        "semester 1": "1",
        "first semester": "1",

        "sem 2": "2",
        "semester 2": "2",
        "second semester": "2",

        "sem 3": "3",
        "semester 3": "3",
        "third semester": "3",

        "sem 4": "4",
        "semester 4": "4",
        "fourth semester": "4",

        "sem 5": "5",
        "semester 5": "5",
        "fifth semester": "5",

        "sem 6": "6",
        "semester 6": "6",
        "sixth semester": "6"
    }

    for key, value in semester_map.items():

        if key in message:

            return value

    return None


# ------------------------------------------------------
# Extract Batch
# ------------------------------------------------------

def extract_batch(message):

    pattern = r"(20\d{2})[- ]?(20\d{2})"

    match = re.search(pattern, message)

    if match:

        return f"{match.group(1)}-{match.group(2)}"

    return None


# ------------------------------------------------------
# Extract Course
# ------------------------------------------------------

def extract_course(message):

    message = message.upper()

    if "TYIT" in message or "BSC IT" in message:

        return "TYIT"

    if "TYDS" in message or "DATA SCIENCE" in message:

        return "TYDS"

    return "VSIT"


# ------------------------------------------------------
# Find Result Record
# ------------------------------------------------------

def search_result(db, message):

    semester = extract_semester(message)

    batch = extract_batch(message)

    course = extract_course(message)

    query = db.query(Result).filter(Result.course == course)

    if semester:

        query = query.filter(Result.semester == semester)

    if batch:

        query = query.filter(Result.batch == batch)

    result = query.first()

    if result:

        return result

    # fallback to official result portal

    return (
        db.query(Result)
        .filter(Result.course == "VSIT")
        .first()
    )