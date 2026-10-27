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

# Some FYIT subjects are allocated to different faculty by division. Keep
# these overrides separate from the subject-wide fallback above so teacher
# questions stay scoped to the selected class.
_EXTRA_TEACHERS_BY_DIVISION = {
    ("FYIT", "B", "WP"): "Ashwini K.",
}

# The timetable's ``PR:`` line assigns practical batches to different
# instructors. Keep those assignments separate from the theory fallback so a
# practical timetable row and a "who teaches" query do not report the theory
# instructor by mistake.
_PRACTICAL_TEACHERS = {
    ("FYIT", "A", "IP"): "B1: Dr. Swapna K.; B2: Ketaki G.; B3: Dr. Geeta S.",
    ("FYIT", "A", "WP"): "B1: Ashwini K.; B2: Dr. Swapna K.; B3: Madhavi A.",
    ("FYIT", "A", "DM"): "B1: Janhavi V.; B2: Maitreyi J.; B3: Prabal D.",
    ("FYIT", "B", "IP"): "B4: Seema V.; B5: Janhvi V.; B6: Dr. Geeta S.",
    ("FYIT", "B", "WP"): "B4: Ashwini K.; B5: Madhavi A.; B6: Seema V.",
    ("FYIT", "B", "DM"): "B4: Amraja S.; B5: Prabal D.; B6: Amraja S.",
    ("FYIT", "C", "IP"): "B6: Dr. Geeta S.; B7: Dr. Swapna K.; B8: Janhavi V G.",
    ("FYIT", "C", "WP"): "B6: Seema M.; B7: Seema V.; B8: Akshatha J.",
    ("FYIT", "C", "DM"): "B6: Amraja S.; B7: Mataprasad C.; B8: Pooja S.",
    ("FYIT", "D", "IP"): "B8: Janhavi V.; B9: Dr. Geeta S.; B10: Ashwini K.",
    ("FYIT", "D", "WP"): "B8: Akshatha J.; B9: Seema M.; B10: Seema V.",
    ("FYIT", "D", "DM"): "B8: Pooja S.; B9: Maitreyi J.; B10: Mataprasad C.",
    ("FYIT", "F", "IP"): "B11: Dr. Swapna K.",
    ("FYIT", "F", "WP"): "B11: Madhavi A.",
    ("FYIT", "F", "DM"): "B11: Rahul S.",
    ("SYIT", "A", "PP"): "B1: Ashwini K.; B2: Rajendra P.",
    ("SYIT", "A", "DS"): "B1: Janhavi V.; B2: Dr. Kimaya S.",
    ("SYIT", "A", "SM"): "B1: Daniel P.; B2: Sarika D.",
    ("SYIT", "B", "PP"): "B3: Rohini D.; B4: Rajendra P.",
    ("SYIT", "B", "DS"): "B3: Akshatha J.; B4: Madhavi A.",
    ("SYIT", "B", "SM"): "B3: Sarika D.; B4: Daniel P.; B5: Daniel P.",
    ("SYIT", "C", "PP"): "B5: Rishabh Y.; B6: Rohini D.; B7: Rajendra P.",
    ("SYIT", "C", "DS"): "B5: Dr. Kimaya S.; B6: Khushi K.; B7: Akshatha J.",
    ("SYIT", "C", "SM"): "B5: Daniel P.; B6: Mataprasad C.; B7: Sarika D.",
    ("SYIT", "D", "PP"): "B7: Rajendra P.; B8: Snehal T.; B9: Rishabh Y.",
    ("SYIT", "D", "DS"): "B7: Akshatha J.; B8: Shraddha S.; B9: Akshatha J.",
    ("SYIT", "D", "SM"): "B7: Sarika D.; B8: Dr. Mataprasad C.; B9: Sarika D.",
    ("SYIT", "E", "PP"): "B10: Snehal T.",
    ("SYIT", "E", "DS"): "B10: Khushi K.",
    ("SYIT", "E", "SM"): "B10: Mataprasad C.",
    ("SYIT", "F", "PP"): "B11: Rohini D.",
    ("SYIT", "F", "DS"): "B11: Madhavi A.",
    ("SYIT", "F", "SM"): "B11: Dr. Laxmikant M.",
}

# Some source cells continue onto the next period and therefore do not repeat
# their batch label in the OCR room field. These keys preserve the batch scope
# from the printed cell so a continuation row does not inherit extra faculty.
_PRACTICAL_ROW_BATCHES = {
    ("SYIT", "B", "Monday", "PP", "1:30 pm"): ("B3",),
    ("SYIT", "B", "Wednesday", "SM", "12:30 pm"): ("B3", "B4"),
    ("SYIT", "B", "Tuesday", "PP", "12:30 pm"): ("B4",),
}


def _practical_teacher_for_row(row):
    import re

    key = (row["course"], row["division"], row["subject"])
    value = _PRACTICAL_TEACHERS.get(key)
    if not value:
        return ""
    batches = _PRACTICAL_ROW_BATCHES.get(
        (row["course"], row["division"], row["day"], row["subject"], row["start_time"])
    )
    if not batches:
        batches = tuple(re.findall(r"B\d+", row.get("room", "")))
    if not batches:
        return value
    entries = dict(re.findall(r"(B\d+):\s*([^;]+)", value))
    return "; ".join(f"{batch}: {entries[batch]}" for batch in batches if batch in entries)


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
        practical_key = (row["course"], row["division"], row["subject"])
        if row.get("lecture_type") == "Practical" and practical_key in _PRACTICAL_TEACHERS:
            row["teacher"] = _practical_teacher_for_row(row)
        else:
            row["teacher"] = _EXTRA_TEACHERS_BY_DIVISION.get(
                practical_key,
                _EXTRA_TEACHERS.get(row["course"], {}).get(row["subject"], ""),
            )
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
