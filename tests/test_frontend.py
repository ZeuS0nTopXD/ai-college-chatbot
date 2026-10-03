def test_student_frontend_has_accessible_navigation_and_assistant_controls(client):
    response = client.get("/")

    assert response.status_code == 200
    html = response.text
    assert "<nav" in html
    assert 'data-view="assistant"' in html
    assert 'data-view="academics"' in html
    assert 'data-view="resources"' in html
    assert 'aria-label="Ask the VSIT assistant"' in html
    assert 'aria-live="polite"' in html
    assert 'id="voice-button"' in html
    assert 'id="speech-toggle"' in html


def test_student_frontend_uses_relative_api_urls_and_progressive_voice(client):
    response = client.get("/script.js")

    assert response.status_code == 200
    script = response.text
    assert "http://127.0.0.1:8000" not in script
    assert 'fetch("/chat"' in script
    assert 'fetch("/api/academics"' in script
    assert 'fetch("/api/documents"' in script
    assert "SpeechRecognition" in script
    assert "speechSynthesis" in script


def test_admin_frontend_contains_login_management_and_upload_controls(client):
    response = client.get("/admin")

    assert response.status_code == 200
    html = response.text
    assert 'id="admin-login-form"' in html
    assert 'id="academic-form"' in html
    assert 'id="knowledge-form"' in html
    assert 'id="faculty-form"' in html
    assert 'id="office-form"' in html
    assert 'id="document-form"' in html
    assert 'type="file"' in html


def test_frontend_styles_include_keyboard_focus_and_mobile_layout(client):
    response = client.get("/style.css")

    assert response.status_code == 200
    assert ":focus-visible" in response.text
    assert "@media (max-width:" in response.text
