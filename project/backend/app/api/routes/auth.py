"""Dashboard authentication — login and current-user endpoints.

The dashboard is an operator UI: accounts are seeded at startup from
DASHBOARD_ADMIN_USERNAME/PASSWORD (see app/services/dashboard_auth.py).
A successful login returns a JWT (Authorization: Bearer …) that guards
every cross-tenant admin endpoint.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.dependencies import require_dashboard_user
from app.core.config import settings
from app.core.database import get_db
from app.core.ratelimit import limiter
from app.core.security import create_dashboard_token, verify_password
from app.models import User
from app.repositories.user_repo import UserRepository
from app.schemas.auth import LoginRequest, TokenResponse, UserMeResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
@limiter.limit(lambda: f"{settings.dashboard_login_per_minute}/minute")
def login(
    body: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Exchange username/password for a dashboard JWT.

    Always answers 401 "Identifiants invalides" (never reveals whether
    the username exists). Rate-limited to 5 attempts/minute per client.
    """
    repo = UserRepository(db)
    user = repo.get_by_username(body.username)
    if user is None or not user.is_active or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token, ttl_seconds = create_dashboard_token(user.id, user.username)
    return TokenResponse(access_token=token, expires_in=ttl_seconds, username=user.username)


@router.get("/me", response_model=UserMeResponse)
def get_me(user: User = Depends(require_dashboard_user)) -> UserMeResponse:
    """Return the connected dashboard user (token validation probe)."""
    return UserMeResponse(id=user.id, username=user.username)
