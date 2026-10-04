from backend.data.official_vsit_data import OFFICIAL_KNOWLEDGE_DATA
from backend.database.database import SessionLocal
from backend.models.knowledge import KnowledgeBase


def seed_knowledge():
    db = SessionLocal()
    try:
        for category in ("VSIT", "OFFICE", "FACULTY"):
            db.query(KnowledgeBase).filter(
                KnowledgeBase.category == category
            ).delete(synchronize_session=False)
        db.add_all(KnowledgeBase(**item) for item in OFFICIAL_KNOWLEDGE_DATA)
        db.commit()
        print(f"Loaded {len(OFFICIAL_KNOWLEDGE_DATA)} verified VSIT records.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_knowledge()
