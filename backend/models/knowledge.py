from sqlalchemy import Column, Integer, String, Text
from backend.database.database import Base


class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"

    id = Column(Integer, primary_key=True, index=True)

    category = Column(String(50), nullable=False)

    topic = Column(String(100), nullable=False)

    question = Column(Text, nullable=False)

    answer = Column(Text, nullable=False)