from sqlalchemy import Column, Integer, String, Text
from backend.database.database import Base


class Result(Base):

    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)

    course = Column(String(50), nullable=False)

    semester = Column(String(20), nullable=False)

    batch = Column(String(30), nullable=True)

    year = Column(String(10), nullable=True)

    title = Column(Text, nullable=False)

    url = Column(Text, nullable=False)