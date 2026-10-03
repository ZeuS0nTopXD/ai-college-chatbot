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


def require_admin(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> None:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired administrator token.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthorized

    settings: Settings = request.app.state.settings
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.token_secret,
            algorithms=["HS256"],
        )
    except jwt.InvalidTokenError as exc:
        raise unauthorized from exc

    if payload.get("sub") != "admin":
        raise unauthorized
