from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.dependencies import get_db
from backend.models.student import StudentUser
from backend.schemas.auth import LoginRequest, StudentLoginRequest, StudentRegisterRequest, TokenResponse
from backend.schemas.student import StudentAuthResponse, StudentPublic
from backend.security import (
    create_access_token,
    create_student_access_token,
    hash_password,
    password_matches,
    require_admin,
    require_student,
    verify_password,
)


router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request):
    settings = request.app.state.settings
    if not password_matches(settings, payload.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid administrator credentials.",
        )
    return TokenResponse(access_token=create_access_token(settings))


@router.get("/me", dependencies=[Depends(require_admin)])
def current_admin():
    return {"role": "admin"}


def _student_response(user: StudentUser, request: Request) -> StudentAuthResponse:
    return StudentAuthResponse(
        access_token=create_student_access_token(request.app.state.settings, user.id),
        user=StudentPublic.model_validate(user),
    )


@router.post("/register", response_model=StudentAuthResponse, status_code=status.HTTP_201_CREATED)
def register_student(
    payload: StudentRegisterRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    email = payload.email.strip().lower()
    if db.query(StudentUser).filter(StudentUser.email == email).first() is not None:
        raise HTTPException(status_code=409, detail="An account with that email already exists.")
    user = StudentUser(
        name=payload.name.strip(),
        email=email,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="An account with that email already exists.") from exc
    return _student_response(user, request)


@router.post("/student-login", response_model=StudentAuthResponse)
def login_student(
    payload: StudentLoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    user = db.query(StudentUser).filter(StudentUser.email == payload.email.strip().lower()).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid student credentials.")
    return _student_response(user, request)


@router.get("/student-me", response_model=StudentPublic)
def student_me(student_id: int = Depends(require_student), db: Session = Depends(get_db)):
    user = db.get(StudentUser, student_id)
    if user is None:
        raise HTTPException(status_code=401, detail="Student account no longer exists.")
    return user
