from pathlib import Path


FRONTEND = Path(__file__).parents[1] / "frontend"


def test_student_page_has_account_and_feedback_controls():
    html = (FRONTEND / "index.html").read_text(encoding="utf-8")
    script = (FRONTEND / "script.js").read_text(encoding="utf-8")

    assert 'id="student-login-button"' in html
    assert 'id="student-register-button"' in html
    assert 'data-view="feedback"' in html
    assert 'id="feedback-form"' in html
    assert 'class="account-button admin-login-link" href="/admin"' in html
    assert '"/api/auth/register"' in script
    assert '"/api/auth/student-login"' in script
    assert '"/api/feedback"' in script


def test_admin_page_has_feedback_review_controls():
    html = (FRONTEND / "admin.html").read_text(encoding="utf-8")
    script = (FRONTEND / "admin.js").read_text(encoding="utf-8")

    assert 'data-admin-view="feedback"' in html
    assert 'data-admin-panel="feedback"' in html
    assert 'adminFetch("/api/admin/feedback")' in script
