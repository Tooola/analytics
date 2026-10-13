"""Shared API dependencies — database session, API key auth, dashboard JWT, pagination."""

from __future__ import annotations

import jwt as pyjwt
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_dashboard_token
from app.models import Application, User
from app.repositories.application_repo import ApplicationRepository


def get_pagination(skip: int = 0, limit: int = 100) -> dict:
    """Common pagination params."""
    if skip < 0 or limit < 1 or limit > 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="skip must be >= 0 and limit must be between 1 and 500",
        )
    return {"skip": skip, "limit": limit}


def get_application_by_api_key(
    x_api_key: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> Application:
    """Authenticate the request via X-API-Key header.

    The key is hashed and compared against stored hashes. If the key is
    missing or invalid, a 401 is returned.
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header",
        )
    repo = ApplicationRepository(db)
    app = repo.get_by_api_key(x_api_key)
    if app is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked API key",
        )
    return app


def require_dashboard_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    """Authenticate a dashboard operator via `Authorization: Bearer <JWT>`.

    Guards every cross-tenant (admin) endpoint: the React dashboard login
    exchanges username/password for this token (POST /auth/login).
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token — log in via POST /api/v1/auth/login",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = decode_dashboard_token(token)
    except pyjwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if payload.get("type") != "dashboard":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )
    user = db.get(User, str(payload.get("sub", "")))
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unknown or disabled user",
        )
    return user
