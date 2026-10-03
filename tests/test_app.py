from dataclasses import replace

import pytest


def test_health_endpoint_reports_ready(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


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
