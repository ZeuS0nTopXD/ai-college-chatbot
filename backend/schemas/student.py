from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StudentPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str


class StudentAuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: StudentPublic


class StudentCreated(StudentPublic):
    created_at: datetime
