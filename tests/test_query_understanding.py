import pytest

from backend.services.query_understanding import expand_query, normalize_query


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("  Who’s   the H.O.D.? ", "who s the h o d"),
        ("What’s the timetable for TY-IT?", "what s the timetable for ty it"),
    ],
)
def test_normalize_query_handles_unicode_punctuation_and_spacing(raw, expected):
    assert normalize_query(raw) == expected


def test_expand_query_adds_student_language_aliases():
    expanded = expand_query("who runs the IT department")

    assert "information technology" in expanded
    assert "head of department" in expanded


def test_normalize_query_repairs_common_student_typos():
    assert normalize_query("wht is the hod of computng") == "what is the hod of computing"


def test_normalize_query_understands_common_hinglish_words():
    assert normalize_query("kaun hai computing ka hod") == "who hai computing ka hod"
    assert normalize_query("mere classes kab hain") == "my classes when hain"
    assert normalize_query("VSIT kuthe aahe") == "vsit where aahe"
