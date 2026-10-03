from pydantic import BaseModel, ConfigDict, Field


class KnowledgeCreate(BaseModel):
    category: str = Field(min_length=1, max_length=50)
    topic: str = Field(min_length=1, max_length=100)
    question: str = Field(min_length=1)
    answer: str = Field(min_length=1)


class KnowledgeUpdate(BaseModel):
    category: str | None = Field(default=None, min_length=1, max_length=50)
    topic: str | None = Field(default=None, min_length=1, max_length=100)
    question: str | None = Field(default=None, min_length=1)
    answer: str | None = Field(default=None, min_length=1)


class KnowledgeRead(KnowledgeCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
