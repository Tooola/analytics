"""Application registry CRUD endpoints.

Security model:
- POST /applications  → Public. Required for initial onboarding (register once, get key).
- All other endpoints → Require X-API-Key authentication.
  An application can only read/modify/delete itself (ownership enforced).
  Cross-tenant access returns 404 (never 403) to avoid confirming existence.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_application_by_api_key, get_pagination
from app.core.database import get_db
from app.models import Application
from app.repositories.application_repo import ApplicationRepository
from app.schemas.application import (
    ApplicationCreate,
    ApplicationRead,
    ApplicationUpdate,
    ApplicationWithKey,
)

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("", response_model=ApplicationWithKey, status_code=status.HTTP_201_CREATED)
def create_application(
    body: ApplicationCreate,
    db: Session = Depends(get_db),
) -> ApplicationWithKey:
    """Register a new application and receive an API key (shown only once).

    This endpoint is intentionally public — it is the onboarding entry point.
    The returned api_key must be stored securely in the client backend's
    environment variables. It will not be retrievable again.
    """
    repo = ApplicationRepository(db)
    existing = repo.get_by_slug(
        __import__("app.repositories.application_repo", fromlist=["_slugify"])._slugify(body.name)
    )
    if existing:
        raise HTTPException(status_code=409, detail="Application with this name already exists")
    app, raw_key = repo.create_with_key(name=body.name, description=body.description)
    return ApplicationWithKey(
        id=app.id,
        name=app.name,
        slug=app.slug,
        description=app.description,
        status=app.status,
        created_at=app.created_at,
        updated_at=app.updated_at,
        api_key=raw_key,
    )


@router.get("", response_model=list[ApplicationRead])
def list_applications(
    authed_app: Application = Depends(get_application_by_api_key),
) -> list[ApplicationRead]:
    """List the applications visible to the caller.

    Requires X-API-Key: the listing must not expose other tenants'
    application names/slugs to anonymous callers. Only the authenticated
    application is returned (tenant isolation, consistent with /datasets).
    """
    return [ApplicationRead.model_validate(authed_app)]



@router.get("/me", response_model=ApplicationRead)
def get_own_application(
    authed_app: Application = Depends(get_application_by_api_key),
) -> ApplicationRead:
    """Return the profile of the currently authenticated application."""
    return ApplicationRead.model_validate(authed_app)


@router.put("/me", response_model=ApplicationRead)
def update_own_application(
    body: ApplicationUpdate,
    db: Session = Depends(get_db),
    authed_app: Application = Depends(get_application_by_api_key),
) -> ApplicationRead:
    """Update the profile of the currently authenticated application."""
    repo = ApplicationRepository(db)
    update_data = body.model_dump(exclude_unset=True)
    app = repo.update(authed_app, **update_data)
    return ApplicationRead.model_validate(app)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_own_application(
    db: Session = Depends(get_db),
    authed_app: Application = Depends(get_application_by_api_key),
) -> None:
    """Delete the currently authenticated application and all its data."""
    repo = ApplicationRepository(db)
    repo.delete(authed_app)


@router.post("/me/regenerate-key", response_model=dict)
def regenerate_own_api_key(
    db: Session = Depends(get_db),
    authed_app: Application = Depends(get_application_by_api_key),
) -> dict:
    """Issue a new API key for the authenticated application.

    The old key is immediately invalidated. The new key is returned
    exactly once — store it securely in your backend environment variables.
    """
    repo = ApplicationRepository(db)
    raw_key = repo.regenerate_key(authed_app)
    return {"api_key": raw_key}


@router.post("/me/revoke-key", status_code=status.HTTP_204_NO_CONTENT)
def revoke_own_api_key(
    db: Session = Depends(get_db),
    authed_app: Application = Depends(get_application_by_api_key),
) -> None:
    """Revoke the API key of the authenticated application (disables API access)."""
    repo = ApplicationRepository(db)
    repo.revoke_key(authed_app)


# ─── Administrative / By ID Endpoints ────────────────────────────────────────

def _ensure_ownership(authed_app: Application, app_id: str) -> None:
    """Reject cross-tenant access with 404 (never 403): never confirm existence."""
    if authed_app.id != app_id:
        raise HTTPException(status_code=404, detail="Application not found")


@router.get("/{app_id}", response_model=ApplicationRead)
def get_application_by_id(
    app_id: str,
    authed_app: Application = Depends(get_application_by_api_key),
) -> ApplicationRead:
    """Retrieve an application by ID — own application only."""
    _ensure_ownership(authed_app, app_id)
    return ApplicationRead.model_validate(authed_app)


@router.delete("/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application_by_id(
    app_id: str,
    db: Session = Depends(get_db),
    authed_app: Application = Depends(get_application_by_api_key),
) -> None:
    """Delete an application by ID — own application only."""
    _ensure_ownership(authed_app, app_id)
    repo = ApplicationRepository(db)
    repo.delete(authed_app)


@router.post("/{app_id}/regenerate-key", response_model=dict)
def regenerate_api_key_by_id(
    app_id: str,
    db: Session = Depends(get_db),
    authed_app: Application = Depends(get_application_by_api_key),
) -> dict:
    """Issue a new API key for application identified by app_id — own only."""
    _ensure_ownership(authed_app, app_id)
    repo = ApplicationRepository(db)
    raw_key = repo.regenerate_key(authed_app)
    return {"api_key": raw_key}


@router.post("/{app_id}/revoke-key", status_code=status.HTTP_204_NO_CONTENT)
def revoke_api_key_by_id(
    app_id: str,
    db: Session = Depends(get_db),
    authed_app: Application = Depends(get_application_by_api_key),
) -> None:
    """Revoke the API key for application identified by app_id — own only."""
    _ensure_ownership(authed_app, app_id)
    repo = ApplicationRepository(db)
    repo.revoke_key(authed_app)

