from sqlalchemy import Column, Integer, String, Date, Time, Text, TIMESTAMP
from sqlalchemy.sql import text

from backend.database.database import Base


class Timetable(Base):

    __tablename__ = "timetable"

    # =========================================================
    # PRIMARY KEY
    # =========================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )

    # =========================================================
    # ACADEMIC INFORMATION
    # =========================================================

    academic_year = Column(
        String(20),
        nullable=False,
        default="2026-27"
    )

    semester = Column(
        String(50),
        nullable=False,
        default="Odd Semester"
    )

    effective_from = Column(
        Date,
        nullable=True
    )

    # =========================================================
    # COURSE / DIVISION
    # =========================================================

    course = Column(
        String(100),
        nullable=False,
        default="B.Sc. Information Technology"
    )

    division = Column(
        String(10),
        nullable=False
    )

    # =========================================================
    # DAY / TIME
    # =========================================================

    day = Column(
        String(20),
        nullable=False
    )

    start_time = Column(
        Time,
        nullable=False
    )

    end_time = Column(
        Time,
        nullable=False
    )

    # =========================================================
    # SUBJECT INFORMATION
    # =========================================================

    subject_code = Column(
        String(30),
        nullable=False
    )

    subject_name = Column(
        String(150),
        nullable=True
    )

    # =========================================================
    # ROOM / SESSION
    # =========================================================

    room = Column(
        String(100),
        nullable=True
    )

    session_type = Column(
        String(30),
        nullable=True,
        default="Theory"
    )

    # =========================================================
    # TEACHER
    # =========================================================

    teacher_names = Column(
        Text,
        nullable=True
    )

    # =========================================================
    # CREATED DATE
    # =========================================================

    created_at = Column(
        TIMESTAMP,
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP")
    )

    # =========================================================
    # COMPATIBILITY PROPERTIES
    #
    # Your existing chat.py uses:
    #
    # item.subject
    # item.teacher
    # item.lecture_type
    #
    # Instead of changing hundreds of lines in chat.py,
    # these properties map the old names to the real database
    # columns.
    # =========================================================

    @property
    def subject(self):
        return self.subject_name

    @property
    def teacher(self):
        return self.teacher_names

    @property
    def lecture_type(self):
        return self.session_type