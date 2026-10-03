from sqlalchemy.orm import Session

from backend.models.office import Office


# ============================================================
# GET ALL ACTIVE OFFICES
# ============================================================

def get_all_offices(db: Session):
    return (
        db.query(Office)
        .filter(Office.is_active.is_(True))
        .order_by(Office.office_name.asc())
        .all()
    )


# ============================================================
# GET OFFICE BY EXACT NAME
# ============================================================

def get_office_by_name(
    db: Session,
    office_name: str
):
    if not office_name:
        return None

    return (
        db.query(Office)
        .filter(
            Office.office_name.ilike(office_name),
            Office.is_active.is_(True)
        )
        .first()
    )


# ============================================================
# GET OFFICE BY KEYWORD
# ============================================================
def get_office_by_keyword(
    db: Session,
    keyword: str
):
    """
    Find a specific office using a user keyword or phrase.

    Examples:
        admission
        admission office
        placement
        placement cell
        examination
        examination cell
        accounts
        accounts office
        bonafide
        certificate
    """

    if not keyword:
        return None

    keyword = keyword.strip().lower()

    # --------------------------------------------------------
    # Map user terminology to official office names
    # --------------------------------------------------------

    office_mapping = {
        # Admission
        "admission": "Admission Office",
        "admissions": "Admission Office",
        "admission office": "Admission Office",
        "admissions office": "Admission Office",

        # Placement
        "placement": "Placement Cell",
        "placements": "Placement Cell",
        "placement cell": "Placement Cell",
        "placements cell": "Placement Cell",

        # Examination
        "examination": "Examination Cell",
        "examinations": "Examination Cell",
        "exam": "Examination Cell",
        "exams": "Examination Cell",
        "exam cell": "Examination Cell",
        "examination cell": "Examination Cell",

        # Accounts
        "account": "Accounts Office",
        "accounts": "Accounts Office",
        "account office": "Accounts Office",
        "accounts office": "Accounts Office",
        "fees": "Accounts Office",
        "fee": "Accounts Office",

        # Student Section
        "student": "Student Section",
        "student section": "Student Section",
        "student office": "Student Section",
        "bonafide": "Student Section",
        "bonafide certificate": "Student Section",
        "certificate": "Student Section",
    }

    # --------------------------------------------------------
    # Direct mapping
    # --------------------------------------------------------

    office_name = office_mapping.get(keyword)

    if office_name:
        office = (
            db.query(Office)
            .filter(
                Office.office_name.ilike(office_name),
                Office.is_active.is_(True)
            )
            .first()
        )

        if office:
            return office

    # --------------------------------------------------------
    # Fallback database search
    # --------------------------------------------------------

    search = f"%{keyword}%"

    return (
        db.query(Office)
        .filter(
            Office.is_active.is_(True),
            (
                Office.office_name.ilike(search)
                | Office.department.ilike(search)
                | Office.purpose.ilike(search)
                | Office.location.ilike(search)
                | Office.procedure_details.ilike(search)
            )
        )
        .order_by(Office.id.asc())
        .first()
    )


# ============================================================
# SEARCH OFFICES
# ============================================================

def search_offices(
    db: Session,
    keyword: str
):
    if not keyword:
        return []

    search = f"%{keyword}%"

    return (
        db.query(Office)
        .filter(
            Office.is_active.is_(True),
            (
                Office.office_name.ilike(search)
                | Office.department.ilike(search)
                | Office.purpose.ilike(search)
                | Office.location.ilike(search)
                | Office.procedure_details.ilike(search)
            )
        )
        .order_by(Office.office_name.asc())
        .all()
    )


# ============================================================
# FORMAT OFFICE
# ============================================================

def format_office(office: Office):

    if not office:
        return None

    return {
        "id": office.id,
        "office_name": office.office_name,
        "department": office.department,
        "purpose": office.purpose,
        "timings": office.timings,
        "location": office.location,
        "contact_person": office.contact_person,
        "contact_email": office.contact_email,
        "contact_phone": office.contact_phone,
        "procedure_details": office.procedure_details,
        "is_active": office.is_active,
    }