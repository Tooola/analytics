"""Dataset repository — manages datasets and their field definitions."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Dataset, DatasetField
from app.repositories.base import BaseRepository
from app.schemas.dataset import DatasetFieldCreate


class DatasetRepository(BaseRepository[Dataset]):
    model = Dataset

    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get_with_fields(self, id: str) -> Dataset | None:
        stmt = (
            select(Dataset)
            .options(selectinload(Dataset.fields))
            .where(Dataset.id == id)
        )
        return self.db.scalars(stmt).first()

    def get_by_slug(self, application_id: str, slug: str) -> Dataset | None:
        stmt = (
            select(Dataset)
            .options(selectinload(Dataset.fields))
            .where(Dataset.application_id == application_id, Dataset.slug == slug)
        )
        return self.db.scalars(stmt).first()

    def list_by_application(self, application_id: str) -> list[Dataset]:
        stmt = (
            select(Dataset)
            .options(selectinload(Dataset.fields))
            .where(Dataset.application_id == application_id)
            .order_by(Dataset.name)
        )
        return list(self.db.scalars(stmt))

    def create_with_fields(
        self,
        application_id: str,
        name: str,
        slug: str,
        description: str | None,
        fields: list[DatasetFieldCreate],
    ) -> Dataset:
        dataset = Dataset(
            application_id=application_id,
            name=name,
            slug=slug,
            description=description,
        )
        self.db.add(dataset)
        self.db.flush()  # get the id without committing

        for f in fields:
            self.db.add(
                DatasetField(
                    dataset_id=dataset.id,
                    name=f.name,
                    technical_type=f.technical_type,
                    semantic_type=f.semantic_type,
                    unit=f.unit,
                    required=f.required,
                    description=f.description,
                )
            )
        self.db.commit()
        self.db.refresh(dataset)
        # Reload fields relationship
        return self.get_with_fields(dataset.id)  # type: ignore[return-value]
