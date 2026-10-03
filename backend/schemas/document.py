from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    category: str
    filename: str
    page_count: int
    status: str
    created_at: datetime


class DocumentSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)
    limit: int = Field(default=4, ge=1, le=10)


class DocumentSearchHit(BaseModel):
    document_id: int
    title: str
    category: str
    page: int
    excerpt: str
    score: float


class DocumentSearchResponse(BaseModel):
    hits: list[DocumentSearchHit]
