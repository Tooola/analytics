"""Analysis run and insight repository."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import AnalysisRun, Insight
from app.repositories.base import BaseRepository


class AnalysisRunRepository(BaseRepository[AnalysisRun]):
    model = AnalysisRun

    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get_with_insights(self, id: str) -> AnalysisRun | None:
        stmt = (
            select(AnalysisRun)
            .options(selectinload(AnalysisRun.insights))
            .where(AnalysisRun.id == id)
        )
        return self.db.scalars(stmt).first()

    def list_recent(self, limit: int = 50) -> list[AnalysisRun]:
        stmt = (
            select(AnalysisRun)
            .order_by(AnalysisRun.created_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt))

    def list_by_application(self, application_id: str, limit: int = 50) -> list[AnalysisRun]:
        """Return recent analysis runs scoped to a specific application."""
        stmt = (
            select(AnalysisRun)
            .where(AnalysisRun.application_id == application_id)
            .order_by(AnalysisRun.created_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt))

    def create_run(
        self,
        application_id: str,
        dataset_id: str,
        analysis_types: list[str],
        row_count: int,
    ) -> AnalysisRun:
        run = AnalysisRun(
            application_id=application_id,
            dataset_id=dataset_id,
            analysis_types=",".join(analysis_types),
            status="running",
            row_count=row_count,
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    def complete_run(
        self,
        run: AnalysisRun,
        result: dict,
        ai_interpretation: str | None = None,
    ) -> None:
        run.status = "completed"
        run.result = json.dumps(result, default=str)
        run.ai_interpretation = ai_interpretation
        run.completed_at = datetime.now(timezone.utc)
        self.db.commit()

    def fail_run(self, run: AnalysisRun, error: str) -> None:
        run.status = "failed"
        run.error_message = error
        run.completed_at = datetime.now(timezone.utc)
        self.db.commit()

    def add_insights(self, run: AnalysisRun, insights: list[dict]) -> list[Insight]:
        created = []
        for i in insights:
            ins = Insight(
                analysis_run_id=run.id,
                type=i["type"],
                severity=i.get("severity", "medium"),
                title=i["title"],
                description=i["description"],
                metric=i.get("metric"),
                value=i.get("value"),
                unit=i.get("unit"),
                confidence=i.get("confidence", 1.0),
            )
            self.db.add(ins)
            created.append(ins)
        self.db.commit()
        return created


class InsightRepository(BaseRepository[Insight]):
    model = Insight

    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def list_recent(self, limit: int = 50) -> list[Insight]:
        stmt = select(Insight).order_by(Insight.created_at.desc()).limit(limit)
        return list(self.db.scalars(stmt))

    def list_by_run(self, run_id: str) -> list[Insight]:
        stmt = select(Insight).where(Insight.analysis_run_id == run_id)
        return list(self.db.scalars(stmt))

    def list_by_application(self, application_id: str, limit: int = 50) -> list[Insight]:
        """Return recent insights scoped to a specific application (via analysis runs)."""
        stmt = (
            select(Insight)
            .join(AnalysisRun, Insight.analysis_run_id == AnalysisRun.id)
            .where(AnalysisRun.application_id == application_id)
            .order_by(Insight.created_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt))
