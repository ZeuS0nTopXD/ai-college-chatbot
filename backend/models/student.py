from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String

from backend.database.database import Base


class StudentUser(Base):
    __tablename__ = "student_users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(254), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
