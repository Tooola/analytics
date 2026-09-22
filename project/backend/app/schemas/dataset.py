"""Pydantic schemas for datasets and fields."""

from __future__ import annotations

from datetime import datetime

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator

from app.models import DatasetFieldType


class DatasetFieldCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    technical_type: DatasetFieldType = Field(..., validation_alias=AliasChoices("technical_type", "type"))
    semantic_type: str | None = Field(None, max_length=100)
    unit: str | None = Field(None, max_length=50)
    required: bool = True
    description: str | None = None

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name must not be blank")
        return v.strip()


class DatasetFieldRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    technical_type: DatasetFieldType
    semantic_type: str | None
    unit: str | None
    required: bool
    description: str | None


class DatasetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255, pattern=r"^[a-z0-9][-a-z0-9]*$")
    description: str | None = None
    fields: list[DatasetFieldCreate] = Field(..., min_length=1)


class DatasetCreate(DatasetBase):
    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name must not be blank")
        return v.strip()


class DatasetUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None


class DatasetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    application_id: str
    name: str
    slug: str
    description: str | None
    fields: list[DatasetFieldRead] = []
    created_at: datetime
    updated_at: datetime
