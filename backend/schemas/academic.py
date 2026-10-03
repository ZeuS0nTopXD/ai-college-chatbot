from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AcademicEventCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    event_type: str = Field(min_length=1, max_length=50)
    course: str | None = Field(default=None, max_length=100)
    semester: str | None = Field(default=None, max_length=30)
    starts_at: datetime
    ends_at: datetime | None = None
    location: str | None = Field(default=None, max_length=200)
    resource_url: str | None = None
    is_published: bool = False


class AcademicEventUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    event_type: str | None = Field(default=None, min_length=1, max_length=50)
    course: str | None = Field(default=None, max_length=100)
    semester: str | None = Field(default=None, max_length=30)
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    location: str | None = Field(default=None, max_length=200)
    resource_url: str | None = None
    is_published: bool | None = None


class AcademicEventRead(AcademicEventCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
