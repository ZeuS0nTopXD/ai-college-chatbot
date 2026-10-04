from dataclasses import replace

import pytest


def test_health_endpoint_reports_ready(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"


def test_root_serves_frontend(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "VSIT Student Assistant" in response.text


def test_test_database_is_isolated(app, settings, tmp_path):
    database_path = tmp_path / "test.db"

    assert app.state.settings is settings
    assert settings.database_url == f"sqlite:///{database_path}"
    assert database_path.exists()


@pytest.mark.parametrize("field", ["admin_password", "token_secret"])
def test_empty_security_settings_are_rejected(settings, field):
    with pytest.raises(ValueError, match=field):
        replace(settings, **{field: ""})


def test_production_environment_rejects_development_secrets(monkeypatch):
    from backend.config import Settings

    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("ADMIN_PASSWORD", "change-me")
    monkeypatch.setenv("TOKEN_SECRET", "development-secret-change-me-before-deploying")
    with pytest.raises(ValueError, match="ADMIN_PASSWORD"):
        Settings.from_env()


def test_each_database_dependency_call_gets_a_distinct_session(app):
    from backend.database.database import SessionLocal

    first = SessionLocal()
    second = SessionLocal()
    try:
        assert first is not second
    finally:
        first.close()
        second.close()
        if hasattr(SessionLocal, "remove"):
            SessionLocal.remove()
