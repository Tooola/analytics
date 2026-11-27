"""Auth schemas — dashboard login (JWT bearer)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=256)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    username: str
    role: str = "admin"


class UserMeResponse(BaseModel):
    id: str
    username: str
    role: str = "admin"


class UserCreateRequest(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=6, max_length=256)
    role: str = Field(default="admin", pattern="^(superadmin|admin|viewer)$")


class UserUpdateRequest(BaseModel):
    role: str | None = Field(default=None, pattern="^(superadmin|admin|viewer)$")
    is_active: bool | None = None
    password: str | None = Field(default=None, min_length=6, max_length=256)


class UserRead(BaseModel):
    id: str
    username: str
    role: str
    is_active: bool
    created_at: datetime
    created_by: str | None = None
