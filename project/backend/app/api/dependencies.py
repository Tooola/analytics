"""Shared API dependencies — database session, API key auth, pagination."""

from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Application
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
