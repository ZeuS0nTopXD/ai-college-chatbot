from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class FeedbackCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    message: str = Field(min_length=5, max_length=2000)
    context: str | None = Field(default=None, max_length=80)

    @field_validator("message")
    @classmethod
    def trim_message(cls, value: str):
        value = value.strip()
        if len(value) < 5:
            raise ValueError("Feedback message must be at least 5 characters.")
        return value

    @field_validator("context")
    @classmethod
    def trim_context(cls, value: str | None):
        if value is None:
            return None
        value = value.strip()
        return value or None


class FeedbackStatusUpdate(BaseModel):
    status: Literal["new", "reviewed"]


class FeedbackRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    student_name: str
    student_email: str
    rating: int
    message: str
    context: str | None
    status: str
    created_at: datetime
