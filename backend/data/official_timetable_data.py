"""Official TYIT timetable issued by VSIT for Odd Semester 2026-27.

The row layout is transcribed from ``TYIT TT20260711_15203906.pdf``.  The
legacy timetable rows contain the same A-E schedule, so this module adds the
official period metadata without duplicating the large table by hand.
"""

from backend.data.timetable_data import TIMETABLE_DATA


OFFICIAL_TIMETABLE_DATA = [
    {
        "academic_year": "2026-27",
        "semester": "Odd Semester",
        "effective_from": "2026-07-13",
        "course": "B.Sc. Information Technology",
        "division": row["division"],
        "day": row["day"],
        "start_time": row["start_time"],
        "end_time": row["end_time"],
        "subject_code": row["subject"],
        "subject_name": row["subject"],
        "teacher_names": row.get("teacher"),
        "room": row["room"],
        "session_type": row["lecture_type"],
    }
    for row in TIMETABLE_DATA
]
