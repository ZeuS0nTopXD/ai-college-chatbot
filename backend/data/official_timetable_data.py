"""Official TYIT timetable issued by VSIT for Odd Semester 2026-27.

The row layout is transcribed from ``TYIT TT20260711_15203906.pdf``.  The
legacy timetable rows contain the same A-E schedule, so this module adds the
official period metadata without duplicating the large table by hand.
"""

from backend.data.timetable_data import TIMETABLE_DATA
import json
from pathlib import Path


_EXTRA_TIMETABLE_PATH = Path(__file__).with_name("fiit_syit_ocr.json")
_EXTRA_TEACHERS = {
    "FYIT": {
        "IP": "Dr. Geeta S.", "DM": "Rahul S.", "WP": "Seema V.",
        "EMSD-I": "Amraja S.", "CSE": "Niki P.", "IKS": "Dr. Saee V.",
        "Physical Fitness": "Himayawathi G.", "MS/ES": "Shruti K. / Mikhail C.",
    },
    "SYIT": {
        "PP": "Ashwini K.", "DS": "Janhavi V.", "OS": "Rajendra P.",
        "AM": "Pooja S.", "SM": "Sarika D.", "FL": "Swarangi V.",
        "NSS": "Poonam S.", "SPORTS": "Himayawati G.", "MAR/HIN": "Mansira Y.",
    },
}


def _extra_rows():
    if not _EXTRA_TIMETABLE_PATH.exists():
        return []
    rows = json.loads(_EXTRA_TIMETABLE_PATH.read_text(encoding="utf-8"))
    for row in rows:
        for key in ("start_time", "end_time"):
            value = row[key].strip().replace(".", ":")
            if value.lower().endswith(("am", "pm")) and " " not in value:
                value = value[:-2] + " " + value[-2:]
            row[key] = value
        row["teacher"] = _EXTRA_TEACHERS.get(row["course"], {}).get(row["subject"], "")
        row["room"] = row.get("room") or ""
    return rows


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
        # The timetable marks classroom practical periods by the X-103 room
        # annotation; preserve that source convention even when the legacy
        # row label was incomplete.
        "session_type": "Practical" if "X103" in row["room"].replace("-", "") else row["lecture_type"],
    }
    for row in TIMETABLE_DATA
]

OFFICIAL_TIMETABLE_DATA.extend(
    {
        "academic_year": "2026-27",
        "semester": "Odd Semester",
        "effective_from": "2026-07-06" if row["course"] == "FYIT" else "2026-06-29",
        "course": row["course"],
        "division": row["division"],
        "day": row["day"],
        "start_time": row["start_time"],
        "end_time": row["end_time"],
        "subject_code": row["subject"],
        "subject_name": row["subject"],
        "teacher_names": row["teacher"],
        "room": row["room"],
        "session_type": row.get("lecture_type", "Theory"),
    }
    for row in _extra_rows()
)
