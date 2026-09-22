"""Application repository — handles slug generation and API key management."""

from __future__ import annotations

import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import generate_api_key, hash_api_key
from app.models import Application, ApplicationStatus
from app.repositories.base import BaseRepository


def _slugify(name: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", name.lower())).strip("-")


class ApplicationRepository(BaseRepository[Application]):
    model = Application

    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get_by_slug(self, slug: str) -> Application | None:
        stmt = select(Application).where(Application.slug == slug)
        return self.db.scalars(stmt).first()

    def get_by_api_key(self, raw_api_key: str) -> Application | None:
        """Look up an application by a raw API key without exposing the hash."""
        key_hash = hash_api_key(raw_api_key)
        stmt = select(Application).where(
            Application.api_key_hash == key_hash,
            Application.status == ApplicationStatus.active,
        )
        return self.db.scalars(stmt).first()

    def create_with_key(self, name: str, description: str | None = None) -> tuple[Application, str]:
        """Create an application and return (obj, raw_api_key)."""
        raw_key = generate_api_key()
        slug = self._unique_slug(name)
        app = Application(
            name=name,
            slug=slug,
            description=description,
            api_key_hash=hash_api_key(raw_key),
        )
        self.db.add(app)
        self.db.commit()
        self.db.refresh(app)
        return app, raw_key

    def regenerate_key(self, app: Application) -> str:
        """Issue a new API key for *app* and return the raw key."""
        raw_key = generate_api_key()
        app.api_key_hash = hash_api_key(raw_key)
        self.db.commit()
        self.db.refresh(app)
        return raw_key

    def revoke_key(self, app: Application) -> None:
        app.api_key_hash = None
        self.db.commit()

    def _unique_slug(self, name: str) -> str:
        base = _slugify(name)
        if not base:
            base = "app"
        slug = base
        suffix = 2
        while self.get_by_slug(slug) is not None:
            slug = f"{base}-{suffix}"
            suffix += 1
        return slug
