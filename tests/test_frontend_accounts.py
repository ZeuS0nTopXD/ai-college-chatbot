from pathlib import Path


FRONTEND = Path(__file__).parents[1] / "frontend"


def test_student_page_has_account_and_feedback_controls():
    html = (FRONTEND / "index.html").read_text(encoding="utf-8")
    script = (FRONTEND / "script.js").read_text(encoding="utf-8")

    assert 'id="student-login-button"' in html
    assert '<span id="student-account-label">Guest student</span>' in html
    assert 'href="polish.css?v=admin-overview-20261027"' in html
    assert 'id="student-account-label"' in html
    assert 'data-view="history"' in html
    assert 'id="history-view"' in html
    assert 'id="history-list"' in html
    assert 'id="history-clear"' in html
    styles = (FRONTEND / "polish.css").read_text(encoding="utf-8")
    assert ".app-shell .assistant-tools" in styles
    assert ".app-shell .assistant-actions .text-button" in styles
    assert ".app-shell .context-intro .tool-label" in styles
    assert "font:600 14px/1.2 'Plus Jakarta Sans',sans-serif" in styles
    assert ".student-context-form label{display:flex;flex:1;align-items:center" in styles
    assert ".admin-page .overview-counts{grid-template-columns:repeat(2,minmax(0,1fr))" in styles
    assert ".admin-page .overview-count{display:grid;grid-template-columns:auto 1fr;align-items:baseline;gap:12px" in styles
    assert 'id="student-register-button"' in html
    assert 'data-view="feedback"' in html
    assert 'id="feedback-form"' in html
    assert 'class="account-button admin-login-link" href="/admin"' in html
    styles = (FRONTEND / "polish.css").read_text(encoding="utf-8")
    assert ".app-shell .student-account" in styles
    assert ".app-shell .account-button" in styles
    assert "grid-template-columns:80px 220px minmax(0,1fr) auto" in styles
    assert '"/api/auth/register"' in script
    assert '"/api/auth/student-login"' in script
    assert 'localStorage.getItem(studentTokenKey)' in script
    assert 'localStorage.setItem(studentTokenKey' in script
    assert 'localStorage.removeItem(studentTokenKey)' in script
    assert '"/api/feedback"' in script
    assert 'id="student-context-form"' in html
    assert 'id="quick-prompts"' in html
    assert 'id="recent-questions"' in html
    assert 'id="conversation-list"' in html
    assert 'id="new-chat"' in html
    assert 'id="clear-chat"' in html
    assert 'id="download-transcript"' in html
    assert 'payload.course = state.profile.course' in script
    assert 'download-transcript' in script
    assert 'vsitChatHistory' in script
    assert 'renderHistory' in script
    assert 'renderConversationList' in script
    assert 'student-account-label' in script
    assert 'Browser storage is optional' in script
    assert 'data-use-context="true"' in html
    assert 'state.profile.year || state.profile.course' in script
    assert 'value="M.Sc. Information Technology"' not in html
    assert 'id="student-year"' in html
    assert 'id="clear-context"' in html
    assert 'delete state.profile.year' in script
    assert 'option value="FYIT">First year (FYIT)</option>' in html
    assert 'option value="SYIT">Second year (SYIT)</option>' in html
    assert 'option value="F">F</option>' in html
    assert '<link rel="icon" href="favicon.svg"' in html
    assert (FRONTEND / "favicon.svg").exists()
    assert 'script.js?v=student-auth-20261027' in html


def test_quick_prompts_are_actionable_and_context_aware():
    html = (FRONTEND / "index.html").read_text(encoding="utf-8")

    assert 'data-question="What classes do I have today?" data-use-context="true"' in html
    assert 'data-question="Who teaches IOT for my class?" data-use-context="true"' in html
    assert 'data-question="Where can I find the latest exam timetable?"' in html
    assert 'data-question="Where is the library and what are its hours?"' in html


def test_official_timetable_resources_are_bundled():
    links = (FRONTEND.parent / "backend" / "data" / "official_links.py").read_text(encoding="utf-8")

    assert "/assets/timetables/FYIT-odd-semester-2026-27.pdf" in links
    assert "/assets/timetables/SYIT-odd-semester-2026-27.pdf" in links
    assert (FRONTEND / "assets" / "timetables" / "FYIT-odd-semester-2026-27.pdf").exists()
    assert (FRONTEND / "assets" / "timetables" / "SYIT-odd-semester-2026-27.pdf").exists()


def test_admin_page_has_feedback_review_controls():
    html = (FRONTEND / "admin.html").read_text(encoding="utf-8")
    script = (FRONTEND / "admin.js").read_text(encoding="utf-8")
    styles = (FRONTEND / "polish.css").read_text(encoding="utf-8")

    assert '<link rel="icon" href="favicon.svg"' in html
    assert 'data-admin-view="feedback"' in html
    assert 'data-admin-panel="feedback"' in html
    assert 'adminFetch("/api/admin/feedback")' in script
    assert 'data-admin-view="dashboard"' in html
    assert 'data-admin-panel="dashboard"' in html
    assert 'id="overview-counts"' in html
    assert 'adminFetch("/api/admin/overview")' in script
    assert 'href="polish.css?v=admin-overview-20261027"' in html
    assert ".admin-page .overview-count{display:grid;grid-template-columns:auto 1fr;align-items:baseline;gap:12px" in styles


def test_render_requires_explicit_durable_database_url():
    render = (FRONTEND.parent / "render.yaml").read_text(encoding="utf-8")

    assert "      - key: DATABASE_URL" not in render
    assert "sqlite:////app/data/vsit_student_assistant.db" not in render
