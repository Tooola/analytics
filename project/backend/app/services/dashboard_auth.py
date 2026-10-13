"""Dashboard user seeding — env-defined operator accounts created at startup."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.repositories.user_repo import UserRepository

logger = get_logger("dashboard_auth")


def ensure_dashboard_users(db: Session) -> list[str]:
    """Create the account declared via DASHBOARD_ADMIN_USERNAME/PASSWORD.

    Idempotent: an existing username is never touched (rotating the
    password means updating the hash in the DB or wiping the users table
    and restarting). Returns the list of usernames created.
    """
    username = (settings.dashboard_admin_username or "").strip()
    password = settings.dashboard_admin_password or ""
    if not username or not password:
        return []
    repo = UserRepository(db)
    if repo.get_by_username(username) is not None:
        return []
    repo.create_user(username, password)
    logger.info("Dashboard admin user seeded: %s", username)
    return [username]
