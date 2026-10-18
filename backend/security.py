import base64
import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.config import Settings


bearer_scheme = HTTPBearer(auto_error=False)


def password_matches(settings: Settings, supplied_password: str) -> bool:
    return secrets.compare_digest(
        supplied_password.encode("utf-8"),
        settings.admin_password.encode("utf-8"),
    )


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    derived = hashlib.scrypt(
        password.encode("utf-8"), salt=salt, n=16384, r=8, p=1, dklen=64
    )
    return "scrypt$16384$8$1${}${}".format(
        base64.urlsafe_b64encode(salt).decode("ascii"),
        base64.urlsafe_b64encode(derived).decode("ascii"),
    )


def verify_password(password: str, encoded: str) -> bool:
    try:
        scheme, n, r, p, salt_text, hash_text = encoded.split("$", 5)
        if scheme != "scrypt":
            return False
        salt = base64.urlsafe_b64decode(salt_text.encode("ascii"))
        expected = base64.urlsafe_b64decode(hash_text.encode("ascii"))
        actual = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=int(n),
            r=int(r),
            p=int(p),
            dklen=len(expected),
        )
        return secrets.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def create_access_token(
    settings: Settings,
    now: datetime | None = None,
) -> str:
    issued_at = now or datetime.now(timezone.utc)
    payload = {
        "sub": "admin",
        "iat": issued_at,
        "exp": issued_at + timedelta(minutes=settings.token_ttl_minutes),
    }
    return jwt.encode(payload, settings.token_secret, algorithm="HS256")


def create_student_access_token(settings: Settings, student_id: int, now: datetime | None = None) -> str:
    issued_at = now or datetime.now(timezone.utc)
    payload = {
        "sub": str(student_id),
        "role": "student",
        "iat": issued_at,
        "exp": issued_at + timedelta(minutes=settings.token_ttl_minutes),
    }
    return jwt.encode(payload, settings.token_secret, algorithm="HS256")


def _decode_token(request: Request, credentials: HTTPAuthorizationCredentials | None):
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthorized
    settings: Settings = request.app.state.settings
    try:
        return jwt.decode(credentials.credentials, settings.token_secret, algorithms=["HS256"])
    except jwt.InvalidTokenError as exc:
        raise unauthorized from exc


def require_admin(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> None:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired administrator token.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = _decode_token(request, credentials)
    if payload.get("sub") != "admin":
        raise unauthorized


def require_student(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> int:
    payload = _decode_token(request, credentials)
    if payload.get("role") != "student":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A student account is required for this action.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return int(payload["sub"])
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid student token.") from exc
