from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import Session


@pytest.fixture
def auth_context():
    from backend.config import Settings
    from backend.database.database import Base
    from backend.models.feedback import Feedback  # noqa: F401
    from backend.models.student import StudentUser  # noqa: F401

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    settings = Settings(
        database_url="sqlite:///:memory:",
        admin_password="test-admin-password",
        token_secret="test-signing-secret-at-least-32-bytes",
        token_ttl_minutes=30,
        max_upload_bytes=1024,
        document_storage_path=Path("./data/documents"),
        cors_origins=("http://testserver",),
        ollama_url="http://127.0.0.1:9/api/generate",
        ollama_model="test-model",
    )
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(settings=settings)))
    with Session(engine) as db:
        yield settings, request, db


def test_register_returns_student_token_and_public_user(auth_context):
    from backend.routes.auth import register_student
    from backend.schemas.auth import StudentRegisterRequest

    response = register_student(
        StudentRegisterRequest(
            name="Aarav Student",
            email="aarav@example.com",
            password="strong-pass-123",
        ),
        auth_context[1],
        auth_context[2],
    )

    assert response.token_type == "bearer"
    assert response.user.email == "aarav@example.com"
    assert response.user.name == "Aarav Student"
    assert not hasattr(response.user, "password_hash")


def test_registration_normalizes_email_and_rejects_duplicates(auth_context):
    from backend.routes.auth import register_student
    from backend.schemas.auth import StudentRegisterRequest

    payload = StudentRegisterRequest(
        name="Aarav Student", email="AARAV@EXAMPLE.COM", password="strong-pass-123"
    )
    register_student(payload, auth_context[1], auth_context[2])

    with pytest.raises(HTTPException) as error:
        register_student(
            payload.model_copy(update={"email": " aarav@example.com "}),
            auth_context[1],
            auth_context[2],
        )
    assert error.value.status_code == 409


def test_student_login_and_me_require_student_token(auth_context):
    from backend.routes.auth import login_student, register_student, student_me
    from backend.schemas.auth import StudentLoginRequest, StudentRegisterRequest

    registered = register_student(
        StudentRegisterRequest(
            name="Aarav Student", email="aarav@example.com", password="strong-pass-123"
        ),
        auth_context[1],
        auth_context[2],
    )
    logged_in = login_student(
        StudentLoginRequest(email="aarav@example.com", password="strong-pass-123"),
        auth_context[1],
        auth_context[2],
    )

    assert logged_in.user.id == registered.user.id
    assert student_me(registered.user.id, auth_context[2]).email == "aarav@example.com"


def test_student_token_is_rejected_by_admin_dependency(auth_context):
    from backend.routes.auth import register_student
    from backend.schemas.auth import StudentRegisterRequest
    from backend.security import require_admin

    response = register_student(
        StudentRegisterRequest(
            name="Aarav Student", email="aarav@example.com", password="strong-pass-123"
        ),
        auth_context[1],
        auth_context[2],
    )

    with pytest.raises(HTTPException) as error:
        require_admin(
            auth_context[1],
            HTTPAuthorizationCredentials(scheme="Bearer", credentials=response.access_token),
        )
    assert error.value.status_code == 401


def test_registration_rejects_blank_after_trimming(auth_context):
    from backend.schemas.auth import StudentRegisterRequest

    with pytest.raises(ValueError):
        StudentRegisterRequest(name="  ", email="student@example.com", password="strong-pass-123")
