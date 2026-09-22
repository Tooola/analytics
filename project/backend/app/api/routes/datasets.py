"""Dataset registry CRUD endpoints — all require API Key authentication."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_application_by_api_key, get_pagination
from app.core.database import get_db
from app.models import Application
from app.repositories.dataset_repo import DatasetRepository
from app.schemas.dataset import DatasetCreate, DatasetRead, DatasetUpdate

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.post("", response_model=DatasetRead, status_code=status.HTTP_201_CREATED)
def create_dataset(
    body: DatasetCreate,
    db: Session = Depends(get_db),
    app: Application = Depends(get_application_by_api_key),
) -> DatasetRead:
    """Register a new dataset for the authenticated application."""
    dataset_repo = DatasetRepository(db)
    existing = dataset_repo.get_by_slug(app.id, body.slug)
    if existing:
        raise HTTPException(status_code=409, detail="Dataset with this slug already exists")
    dataset = dataset_repo.create_with_fields(
        application_id=app.id,
        name=body.name,
        slug=body.slug,
        description=body.description,
        fields=body.fields,
    )
    return DatasetRead.model_validate(dataset)


@router.get("", response_model=list[DatasetRead])
def list_datasets(
    pagination: dict = Depends(get_pagination),
    db: Session = Depends(get_db),
    app: Application = Depends(get_application_by_api_key),
) -> list[DatasetRead]:
    """List datasets belonging to the authenticated application only."""
    repo = DatasetRepository(db)
    datasets = repo.list_by_application(app.id)
    return [DatasetRead.model_validate(d) for d in datasets]


@router.get("/all", response_model=list[DatasetRead])
def list_all_datasets_admin(
    db: Session = Depends(get_db),
) -> list[DatasetRead]:
    """List all registered datasets across all applications (for dashboard browsing)."""
    repo = DatasetRepository(db)
    datasets = repo.list()
    return [DatasetRead.model_validate(d) for d in datasets]


@router.get("/by-app/{app_slug}", response_model=list[DatasetRead])
def list_datasets_by_app_slug(
    app_slug: str,
    db: Session = Depends(get_db),
) -> list[DatasetRead]:
    """List datasets belonging to a specific application slug (for dashboard browsing)."""
    from app.repositories.application_repo import ApplicationRepository
    app_repo = ApplicationRepository(db)
    app = app_repo.get_by_slug(app_slug)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    repo = DatasetRepository(db)
    datasets = repo.list_by_application(app.id)
    return [DatasetRead.model_validate(d) for d in datasets]



@router.get("/{dataset_id}", response_model=DatasetRead)
def get_dataset(
    dataset_id: str,
    db: Session = Depends(get_db),
    app: Application = Depends(get_application_by_api_key),
) -> DatasetRead:
    """Retrieve a specific dataset — 404 if not found or not owned by the caller."""
    repo = DatasetRepository(db)
    dataset = repo.get_with_fields(dataset_id)
    # Return 404 (not 403) to avoid confirming existence of another app's dataset.
    if dataset is None or dataset.application_id != app.id:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return DatasetRead.model_validate(dataset)


@router.put("/{dataset_id}", response_model=DatasetRead)
def update_dataset(
    dataset_id: str,
    body: DatasetUpdate,
    db: Session = Depends(get_db),
    app: Application = Depends(get_application_by_api_key),
) -> DatasetRead:
    """Update a dataset owned by the authenticated application."""
    repo = DatasetRepository(db)
    dataset = repo.get_with_fields(dataset_id)
    if dataset is None or dataset.application_id != app.id:
        raise HTTPException(status_code=404, detail="Dataset not found")
    update_data = body.model_dump(exclude_unset=True)
    dataset = repo.update(dataset, **update_data)
    return DatasetRead.model_validate(dataset)


@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dataset(
    dataset_id: str,
    db: Session = Depends(get_db),
    app: Application = Depends(get_application_by_api_key),
) -> None:
    """Delete a dataset owned by the authenticated application."""
    repo = DatasetRepository(db)
    dataset = repo.get_with_fields(dataset_id)
    if dataset is None or dataset.application_id != app.id:
        raise HTTPException(status_code=404, detail="Dataset not found")
    repo.delete(dataset)
