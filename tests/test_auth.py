from datetime import datetime, timedelta, timezone

import jwt

def login(client, password="test-admin-password"):
    return client.post("/api/auth/login", json={"password": password})


def test_valid_password_returns_bearer_token(client):
    response = login(client)

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert isinstance(response.json()["access_token"], str)
    assert response.json()["access_token"]


def test_wrong_password_is_rejected_without_echoing_credentials(client):
    response = login(client, "wrong-secret")

    assert response.status_code == 401
    assert "wrong-secret" not in response.text


def test_missing_token_is_rejected(client):
    response = client.get("/api/auth/me")

    assert response.status_code == 401


def test_expired_token_is_rejected(client, settings):
    from backend.security import create_access_token

    expired = create_access_token(
        settings,
        now=datetime.now(timezone.utc) - timedelta(hours=2),
    )

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {expired}"},
    )

    assert response.status_code == 401


def test_malformed_token_is_rejected(client):
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer not-a-jwt"},
    )

    assert response.status_code == 401


def test_wrong_signature_is_rejected(client, settings):
    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {"sub": "admin", "iat": now, "exp": now + timedelta(minutes=10)},
        "different-signing-secret-at-least-32-bytes",
        algorithm="HS256",
    )

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
