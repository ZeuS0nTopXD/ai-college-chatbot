from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def settings(tmp_path: Path):
    from backend.config import Settings

    return Settings(
        database_url=f"sqlite:///{tmp_path / 'test.db'}",
        admin_password="test-admin-password",
        token_secret="test-signing-secret-at-least-32-bytes",
        token_ttl_minutes=30,
        max_upload_bytes=1024 * 1024,
        document_storage_path=tmp_path / "documents",
        cors_origins=("http://testserver",),
        ollama_url="http://127.0.0.1:9/api/generate",
        ollama_model="test-model",
    )


@pytest.fixture
def app(settings):
    from backend.app import create_app

    return create_app(settings)


@pytest.fixture
def client(app):
    with TestClient(app) as test_client:
        yield test_client
