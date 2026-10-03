from sqlalchemy.orm import Session

from backend.models.faculty import Faculty


def get_all_faculty(
    db: Session,
    department: str | None = None
):
    """
    Get all faculty members.
    Optionally filter by department.
    """

    query = db.query(Faculty)

    if department:
        query = query.filter(
            Faculty.department.ilike(f"%{department}%")
        )

    return query.order_by(Faculty.name.asc()).all()


def get_faculty_by_subject(
    db: Session,
    subject: str
):
    """
    Find faculty members who teach a particular subject.
    """

    if not subject:
        return []

    return (
        db.query(Faculty)
        .filter(
            Faculty.subjects.ilike(f"%{subject}%")
        )
        .order_by(Faculty.name.asc())
        .all()
    )


def get_faculty_by_department(
    db: Session,
    department: str
):
    """
    Get faculty members belonging to a department.
    """

    if not department:
        return []

    return (
        db.query(Faculty)
        .filter(
            Faculty.department.ilike(f"%{department}%")
        )
        .order_by(Faculty.name.asc())
        .all()
    )


def get_hod(
    db: Session,
    department: str
):
    """
    Get the officially stored HOD for a department.

    Only records explicitly marked is_hod=True
    are returned.
    """

    if not department:
        return None

    return (
        db.query(Faculty)
        .filter(
            Faculty.department.ilike(f"%{department}%"),
            Faculty.is_hod.is_(True)
        )
        .first()
    )


def get_faculty_by_name(
    db: Session,
    name: str
):
    """
    Search faculty by name.
    """

    if not name:
        return []

    return (
        db.query(Faculty)
        .filter(
            Faculty.name.ilike(f"%{name}%")
        )
        .order_by(Faculty.name.asc())
        .all()
    )


def format_faculty(faculty: Faculty):
    """
    Convert a Faculty SQLAlchemy object
    into a dictionary safe for API/chat responses.
    """

    if not faculty:
        return None

    return {
        "id": faculty.id,
        "name": faculty.name,
        "department": faculty.department,
        "designation": faculty.designation,
        "subjects": faculty.subjects,
        "email": faculty.email,
        "phone": faculty.phone,
        "office_hours": faculty.office_hours,
        "office_location": faculty.office_location,
        "is_hod": faculty.is_hod,
    }