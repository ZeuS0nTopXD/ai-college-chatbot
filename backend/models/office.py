from sqlalchemy import Column, Integer, String, Text, Boolean

from backend.database.database import Base


class Office(Base):
    __tablename__ = "office"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )

    office_name = Column(
        String(150),
        nullable=False
    )

    department = Column(
        String(150),
        nullable=True
    )

    purpose = Column(
        Text,
        nullable=True
    )

    timings = Column(
        String(200),
        nullable=True
    )

    location = Column(
        String(200),
        nullable=True
    )

    contact_person = Column(
        String(150),
        nullable=True
    )

    contact_email = Column(
        String(200),
        nullable=True
    )

    contact_phone = Column(
        String(50),
        nullable=True
    )

    procedure_details = Column(
        Text,
        nullable=True
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True
    )