# =========================================================
# FACULTY MODEL
# VSIT STUDENT ASSISTANT
# =========================================================

from sqlalchemy import Column, Integer, String, Text, Boolean

from backend.database.database import Base


class Faculty(Base):
    __tablename__ = "faculty"

    id = Column(Integer, primary_key=True, index=True)

    # Faculty basic information
    name = Column(String(150), nullable=False, index=True)

    department = Column(String(150), nullable=False, index=True)

    designation = Column(String(150), nullable=True)

    # Subjects taught by faculty
    # Example:
    # "IOT, DBMS, Computer Networks"
    subjects = Column(Text, nullable=True)

    # Contact information
    email = Column(String(200), nullable=True)

    phone = Column(String(30), nullable=True)

    # Office information
    office_hours = Column(String(200), nullable=True)

    # Location / office
    office_location = Column(String(200), nullable=True)

    # HOD flag
    is_hod = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return (
            f"<Faculty("
            f"id={self.id}, "
            f"name='{self.name}', "
            f"department='{self.department}', "
            f"designation='{self.designation}'"
            f")>"
        )