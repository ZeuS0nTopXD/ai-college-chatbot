from backend.scripts.refresh_official_sources import _readable_text


def test_source_refresh_strips_non_content_markup():
    text = _readable_text("<h1>Admissions</h1><script>bad()</script><p>Apply online</p>")
    assert text == "Admissions Apply online"
    assert "bad" not in text
