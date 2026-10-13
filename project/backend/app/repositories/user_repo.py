"""User repository — dashboard operator accounts (username + bcrypt hash)."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        return self.db.scalars(stmt).first()

    def create_user(self, username: str, raw_password: str) -> User:
        """Create an operator account with a bcrypt-hashed password."""
        return self.create(username=username, password_hash=hash_password(raw_password))
