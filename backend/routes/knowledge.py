from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.database import SessionLocal
from backend.models.knowledge import KnowledgeBase
from backend.schemas.knowledge import KnowledgeCreate


router = APIRouter()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post("/knowledge")
def add_knowledge(
    knowledge: KnowledgeCreate,
    db: Session = Depends(get_db)
):

    new_knowledge = KnowledgeBase(
        category=knowledge.category,
        topic=knowledge.topic,
        question=knowledge.question,
        answer=knowledge.answer
    )

    db.add(new_knowledge)
    db.commit()
    db.refresh(new_knowledge)

    return {
        "message": "Knowledge added successfully",
        "id": new_knowledge.id
    }