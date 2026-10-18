from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from backend.database.database import Base


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("student_users.id"), nullable=False, index=True)
    rating = Column(Integer, nullable=False)
    message = Column(Text, nullable=False)
    context = Column(String(80), nullable=True)
    status = Column(String(20), nullable=False, default="new", index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
