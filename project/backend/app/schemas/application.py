"""Pydantic schemas for applications."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import ApplicationStatus


class ApplicationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    status: ApplicationStatus = ApplicationStatus.active


class ApplicationCreate(ApplicationBase):
    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name must not be blank")
        return v.strip()


class ApplicationUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    status: ApplicationStatus | None = None


class ApplicationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str
    description: str | None
    status: ApplicationStatus
    created_at: datetime
    updated_at: datetime


class ApplicationWithKey(ApplicationRead):
    """Returned only at creation time — includes the raw API key once."""

    api_key: str
