from backend.scripts.refresh_official_sources import SOURCE_PAGES, _readable_text


def test_source_refresh_strips_non_content_markup():
    text = _readable_text("<h1>Admissions</h1><script>bad()</script><p>Apply online</p>")
    assert text == "Admissions Apply online"
    assert "bad" not in text


def test_source_refresh_covers_core_programme_and_student_pages():
    assert len(SOURCE_PAGES) >= 12
    assert "VSIT BMS Admissions" in SOURCE_PAGES
    assert "VSIT Student Grievance Committee" in SOURCE_PAGES
