"""SQLAlchemy ORM models for the analytics platform."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    Enum as SAEnum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ApplicationStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"


class DatasetFieldType(str, enum.Enum):
    string = "string"
    integer = "integer"
    float = "float"
    boolean = "boolean"
    date = "date"
    datetime = "datetime"


class AnalysisType(str, enum.Enum):
    summary = "summary"
    trend = "trend"
    anomaly = "anomaly"
    correlation = "correlation"
    distribution = "distribution"
    forecast = "forecast"
    segmentation = "segmentation"


class AnalysisStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class InsightType(str, enum.Enum):
    trend = "trend"
    anomaly = "anomaly"
    risk = "risk"
    forecast = "forecast"
    opportunity = "opportunity"
    recommendation = "recommendation"


class InsightSeverity(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ApplicationStatus] = mapped_column(
        SAEnum(ApplicationStatus, native_enum=False),
        default=ApplicationStatus.active,
        nullable=False,
    )
    api_key_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    datasets: Mapped[list[Dataset]] = relationship(
        back_populates="application", cascade="all, delete-orphan"
    )
    analysis_runs: Mapped[list[AnalysisRun]] = relationship(
        back_populates="application", cascade="all, delete-orphan"
    )


class Dataset(Base):
    __tablename__ = "datasets"
    __table_args__ = (UniqueConstraint("application_id", "slug", name="uq_dataset_app_slug"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id: Mapped[str] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    application: Mapped[Application] = relationship(back_populates="datasets")
    fields: Mapped[list[DatasetField]] = relationship(
        back_populates="dataset", cascade="all, delete-orphan"
    )
    analysis_runs: Mapped[list[AnalysisRun]] = relationship(
        back_populates="dataset", cascade="all, delete-orphan"
    )


class DatasetField(Base):
    __tablename__ = "dataset_fields"
    __table_args__ = (
        UniqueConstraint("dataset_id", "name", name="uq_field_dataset_name"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    technical_type: Mapped[DatasetFieldType] = mapped_column(
        SAEnum(DatasetFieldType, native_enum=False), nullable=False
    )
    semantic_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    required: Mapped[bool] = mapped_column(default=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    dataset: Mapped[Dataset] = relationship(back_populates="fields")


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id: Mapped[str] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True
    )
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    analysis_types: Mapped[str] = mapped_column(Text, nullable=False)  # comma-separated
    status: Mapped[AnalysisStatus] = mapped_column(
        SAEnum(AnalysisStatus, native_enum=False),
        default=AnalysisStatus.pending,
        nullable=False,
    )
    row_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    result: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON blob
    ai_interpretation: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON blob
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    application: Mapped[Application] = relationship(back_populates="analysis_runs")
    dataset: Mapped[Dataset] = relationship(back_populates="analysis_runs")
    insights: Mapped[list[Insight]] = relationship(
        back_populates="analysis_run", cascade="all, delete-orphan"
    )


class Insight(Base):
    __tablename__ = "insights"
    __table_args__ = (Index("ix_insights_run", "analysis_run_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_run_id: Mapped[str] = mapped_column(
        ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type: Mapped[InsightType] = mapped_column(
        SAEnum(InsightType, native_enum=False), nullable=False
    )
    severity: Mapped[InsightSeverity] = mapped_column(
        SAEnum(InsightSeverity, native_enum=False), default=InsightSeverity.medium, nullable=False
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    metric: Mapped[str | None] = mapped_column(String(255), nullable=True)
    value: Mapped[float | None] = mapped_column(Float, nullable=True)
    unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    analysis_run: Mapped[AnalysisRun] = relationship(back_populates="insights")
