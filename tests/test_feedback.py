from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import Session


@pytest.fixture
def feedback_context():
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


def _student(feedback_context):
    from backend.routes.auth import register_student
    from backend.schemas.auth import StudentRegisterRequest

    return register_student(
        StudentRegisterRequest(
            name="Feedback Student",
            email="feedback@example.com",
            password="strong-pass-123",
        ),
        feedback_context[1],
        feedback_context[2],
    )


def test_student_can_submit_feedback_and_admin_can_review_it(feedback_context):
    from backend.routes.admin import list_feedback, update_feedback
    from backend.routes.feedback import create_feedback
    from backend.schemas.feedback import FeedbackCreate, FeedbackStatusUpdate

    student = _student(feedback_context)
    created = create_feedback(
        FeedbackCreate(rating=5, message="The timetable answer was clear.", context="assistant"),
        student.user.id,
        feedback_context[2],
    )

    assert created.status == "new"
    listed = list_feedback(feedback_context[2])
    assert listed[0].message == "The timetable answer was clear."
    updated = update_feedback(
        created.id,
        FeedbackStatusUpdate(status="reviewed"),
        feedback_context[2],
    )
    assert updated.status == "reviewed"


def test_feedback_rejects_invalid_input_and_missing_student(feedback_context):
    from backend.routes.feedback import create_feedback
    from backend.schemas.feedback import FeedbackCreate

    with pytest.raises(HTTPException) as error:
        create_feedback(
            FeedbackCreate(rating=5, message="Valid message"),
            999,
            feedback_context[2],
        )
    assert error.value.status_code == 401

    with pytest.raises(ValueError):
        FeedbackCreate(rating=6, message="bad")
    with pytest.raises(ValueError):
        FeedbackCreate(rating=5, message="     ")
