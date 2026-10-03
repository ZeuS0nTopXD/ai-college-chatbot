from fastapi import APIRouter, Depends, HTTPException, Request, status

from backend.schemas.auth import LoginRequest, TokenResponse
from backend.security import create_access_token, password_matches, require_admin


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
