"""Dashboard user seeding — env-defined operator accounts created at startup."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.repositories.user_repo import UserRepository

logger = get_logger("dashboard_auth")


def ensure_dashboard_users(db: Session) -> list[str]:
    """Create the account declared via DASHBOARD_ADMIN_USERNAME/PASSWORD
    and ensure system application for Quick Tests exists.
    """
    username = (settings.dashboard_admin_username or "").strip()
    password = settings.dashboard_admin_password or ""
    created = []
    if username and password:
        repo = UserRepository(db)
        if repo.get_by_username(username) is None:
            repo.create_user(username, password, role="superadmin")
            logger.info("Dashboard superadmin user seeded: %s", username)
            created.append(username)

    # Ensure system app and dataset for Quick Tests exist
    ensure_system_quick_test_entities(db)
    return created


def ensure_system_quick_test_entities(db: Session) -> tuple[str, str]:
    """Ensure a system Application and Dataset exist to hold Quick Test runs."""
    from app.models import Application, Dataset
    import uuid

    app = db.query(Application).filter(Application.slug == "quick-test").first()
    if not app:
        app = Application(
            id=str(uuid.uuid4()),
            name="Test Rapide",
            slug="quick-test",
            description="Application système pour les analyses du banc d'essai rapide",
            api_key_hash="system_internal",
        )
        db.add(app)
        db.flush()

    dataset = db.query(Dataset).filter(Dataset.slug == "quick-dataset", Dataset.application_id == app.id).first()
    if not dataset:
        dataset = Dataset(
            id=str(uuid.uuid4()),
            application_id=app.id,
            name="Données Rapides",
            slug="quick-dataset",
            description="Dataset système pour les analyses instantanées",
        )
        db.add(dataset)
        db.flush()

    db.commit()
    return app.id, dataset.id

