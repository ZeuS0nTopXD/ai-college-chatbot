from pydantic import BaseModel, ConfigDict, Field


class FacultyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    department: str = Field(min_length=1, max_length=150)
    designation: str | None = Field(default=None, max_length=150)
    subjects: str | None = None
    email: str | None = Field(default=None, max_length=200)
    phone: str | None = Field(default=None, max_length=30)
    office_hours: str | None = Field(default=None, max_length=200)
    office_location: str | None = Field(default=None, max_length=200)
    is_hod: bool = False


class FacultyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    department: str | None = Field(default=None, min_length=1, max_length=150)
    designation: str | None = Field(default=None, max_length=150)
    subjects: str | None = None
    email: str | None = Field(default=None, max_length=200)
    phone: str | None = Field(default=None, max_length=30)
    office_hours: str | None = Field(default=None, max_length=200)
    office_location: str | None = Field(default=None, max_length=200)
    is_hod: bool | None = None


class FacultyRead(FacultyCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class OfficeCreate(BaseModel):
    office_name: str = Field(min_length=1, max_length=150)
    department: str | None = Field(default=None, max_length=150)
    purpose: str | None = None
    timings: str | None = Field(default=None, max_length=200)
    location: str | None = Field(default=None, max_length=200)
    contact_person: str | None = Field(default=None, max_length=150)
    contact_email: str | None = Field(default=None, max_length=200)
    contact_phone: str | None = Field(default=None, max_length=50)
    procedure_details: str | None = None
    is_active: bool = True


class OfficeUpdate(BaseModel):
    office_name: str | None = Field(default=None, min_length=1, max_length=150)
    department: str | None = Field(default=None, max_length=150)
    purpose: str | None = None
    timings: str | None = Field(default=None, max_length=200)
    location: str | None = Field(default=None, max_length=200)
    contact_person: str | None = Field(default=None, max_length=150)
    contact_email: str | None = Field(default=None, max_length=200)
    contact_phone: str | None = Field(default=None, max_length=50)
    procedure_details: str | None = None
    is_active: bool | None = None


class OfficeRead(OfficeCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
