from pydantic import BaseModel


class KnowledgeCreate(BaseModel):
    category: str
    topic: str
    question: str
    answer: str