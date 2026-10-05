"""Regular examination commencement dates from VSIT's 25 August 2026 notice.

The notice gives a commencement date, not individual exam times. Midnight is
only a storage sentinel; the UI and chat must display these as date-only.
"""

from datetime import datetime


SOURCE_URL = "https://vsit.edu.in/wp-content/uploads/2026/08/Notice-for-regular-exam-commencement-dates.pdf"
COMMENCEMENT_DATE = datetime(2026, 10, 12)

# Course names and semester numbers transcribed from the three-page signed PDF.
PROGRAMMES = (
    ("BSc IT", (1, 3, 5)),
    ("BSc Data Science", (1, 3, 5)),
    ("BSc CS (AI/ML)", (1,)),
    ("BCom Accounting & Finance", (1, 3, 5)),
    ("BCom Banking & Insurance", (1, 3, 5)),
    ("BCom Financial Markets", (1, 3, 5)),
    ("BCom Finance & Analytics", (1,)),
    ("BMS", (3, 5)),
    ("BCom Business Administration", (1,)),
    ("BA Multimedia & Mass Communication", (1, 3, 5)),
    ("BA Digital Marketing Communication", (1,)),
)

OFFICIAL_ACADEMIC_EVENTS = [
    {
        "title": f"{course} Semester {semester} regular examinations commence",
        "description": (
            "Winter 2026 regular examination commencement date published by VSIT. "
            "This notice does not specify exam times; check the detailed timetable."
        ),
        "event_type": "examination",
        "course": course,
        "semester": str(semester),
        "starts_at": COMMENCEMENT_DATE,
        "resource_url": SOURCE_URL,
        "is_published": True,
    }
    for course, semesters in PROGRAMMES
    for semester in semesters
]
