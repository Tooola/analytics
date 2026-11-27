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
from app.core.security import create_dashboard_token, hash_password, verify_password
from app.models import User, UserRole
from app.repositories.user_repo import UserRepository
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    UserCreateRequest,
    UserMeResponse,
    UserRead,
    UserUpdateRequest,
)

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
    return TokenResponse(
        access_token=token,
        expires_in=ttl_seconds,
        username=user.username,
        role=user.role.value if hasattr(user.role, "value") else str(user.role),
    )


@router.get("/me", response_model=UserMeResponse)
def get_me(user: User = Depends(require_dashboard_user)) -> UserMeResponse:
    """Return the connected dashboard user (token validation probe)."""
    return UserMeResponse(
        id=user.id,
        username=user.username,
        role=user.role.value if hasattr(user.role, "value") else str(user.role),
    )


# ─── Multi-Admins Management Endpoints ─────────────────────────────────────────

def require_superadmin_user(current_user: User = Depends(require_dashboard_user)) -> User:
    role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if role != UserRole.superadmin.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul un superadmin peut gérer les comptes administrateurs",
        )
    return current_user


@router.get("/users", response_model=list[UserRead])
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_superadmin_user),
) -> list[UserRead]:
    """List all operator accounts."""
    repo = UserRepository(db)
    users = repo.list()
    return [
        UserRead(
            id=u.id,
            username=u.username,
            role=u.role.value if hasattr(u.role, "value") else str(u.role),
            is_active=u.is_active,
            created_at=u.created_at,
            created_by=u.created_by,
        )
        for u in users
    ]


@router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    body: UserCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin_user),
) -> UserRead:
    """Create a new operator account."""
    repo = UserRepository(db)
    if repo.get_by_username(body.username) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"L'utilisateur '{body.username}' existe déjà",
        )
    new_user = repo.create_user(
        username=body.username,
        raw_password=body.password,
        role=body.role,
        created_by=current_user.id,
    )
    return UserRead(
        id=new_user.id,
        username=new_user.username,
        role=new_user.role.value if hasattr(new_user.role, "value") else str(new_user.role),
        is_active=new_user.is_active,
        created_at=new_user.created_at,
        created_by=new_user.created_by,
    )


@router.patch("/users/{user_id}", response_model=UserRead)
def update_user(
    user_id: str,
    body: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin_user),
) -> UserRead:
    """Update role, active status or password for an operator account."""
    repo = UserRepository(db)
    user = repo.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Prevent a superadmin from deactivating themselves
    if user.id == current_user.id and body.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de désactiver votre propre compte",
        )

    if body.role is not None:
        user.role = UserRole(body.role)
    if body.is_active is not None:
        user.is_active = body.is_active
    if body.password is not None:
        user.password_hash = hash_password(body.password)

    db.commit()
    db.refresh(user)
    return UserRead(
        id=user.id,
        username=user.username,
        role=user.role.value if hasattr(user.role, "value") else str(user.role),
        is_active=user.is_active,
        created_at=user.created_at,
        created_by=user.created_by,
    )


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin_user),
) -> None:
    """Soft-delete (deactivate) an operator account."""
    repo = UserRepository(db)
    user = repo.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de désactiver votre propre compte",
        )
    user.is_active = False
    db.commit()
