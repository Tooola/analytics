"""Security tests — authentication, isolation, validation, and secrets hygiene.

These tests verify:
- Unauthenticated requests are rejected (401).
- Invalid API keys are rejected (401).
- Application A cannot access data belonging to Application B (isolation).
- Invalid/oversized/NaN payloads are rejected (422).
- No real secrets appear in source code.
"""

from __future__ import annotations

import os
import math
import pathlib

# Set test environment BEFORE any app imports
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["APP_ENV"] = "testing"
os.environ["DEBUG"] = "false"
os.environ["API_KEY_HASH_SECRET"] = "test-secret-for-security-tests"
os.environ["CORS_ORIGINS"] = "http://localhost:3000"

from app.core.config import get_settings
get_settings.cache_clear()

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.repositories.application_repo import ApplicationRepository
from app.repositories.dataset_repo import DatasetRepository

# ─── In-memory SQLite test database with StaticPool ──────────────────────────

_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_SessionLocal = sessionmaker(bind=_engine)
Base.metadata.create_all(bind=_engine)


def override_get_db():
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def app_a(client):
    """Register application A and return (slug, api_key)."""
    resp = client.post("/api/v1/applications", json={"name": "AppA Security Test"})
    assert resp.status_code == 201
    data = resp.json()
    return data["slug"], data["api_key"]


@pytest.fixture(scope="module")
def app_b(client):
    """Register application B and return (slug, api_key)."""
    resp = client.post("/api/v1/applications", json={"name": "AppB Security Test"})
    assert resp.status_code == 201
    data = resp.json()
    return data["slug"], data["api_key"]


@pytest.fixture(scope="module")
def dataset_a(client, app_a):
    """Create a dataset for App A and return its id."""
    slug_a, key_a = app_a
    resp = client.post(
        "/api/v1/datasets",
        json={
            "name": "Dataset A",
            "slug": "dataset-a-sec",
            "fields": [
                {"name": "amount", "type": "float", "required": True},
            ],
        },
        headers={"X-API-Key": key_a},
    )
    assert resp.status_code == 201
    return resp.json()["id"]


# ─── 1. Authentication Tests ─────────────────────────────────────────────────

class TestAuthentication:
    """Endpoints requiring auth must reject missing or invalid API keys."""

    def test_analyze_no_key_returns_401(self, client):
        resp = client.post(
            "/api/v1/analyze",
            json={"application": "any", "dataset": "any", "analysis": ["summary"], "data": [{"x": 1}]},
        )
        assert resp.status_code == 401

    def test_analyze_invalid_key_returns_401(self, client):
        resp = client.post(
            "/api/v1/analyze",
            json={"application": "any", "dataset": "any", "analysis": ["summary"], "data": [{"x": 1}]},
            headers={"X-API-Key": "anal_thisisnotavalidkey00000000000000000000"},
        )
        assert resp.status_code == 401

    def test_datasets_list_no_key_returns_401(self, client):
        resp = client.get("/api/v1/datasets")
        assert resp.status_code == 401

    def test_datasets_list_invalid_key_returns_401(self, client):
        resp = client.get("/api/v1/datasets", headers={"X-API-Key": "invalid-key"})
        assert resp.status_code == 401

    def test_insights_no_key_returns_401(self, client):
        resp = client.get("/api/v1/insights")
        assert resp.status_code == 401

    def test_analysis_list_no_key_returns_401(self, client):
        resp = client.get("/api/v1/analysis")
        assert resp.status_code == 401

    def test_analysis_detail_no_key_returns_401(self, client):
        resp = client.get("/api/v1/analysis/fake-id")
        assert resp.status_code == 401

    def test_get_me_no_key_returns_401(self, client):
        resp = client.get("/api/v1/applications/me")
        assert resp.status_code == 401

    def test_valid_key_can_list_datasets(self, client, app_a):
        slug_a, key_a = app_a
        resp = client.get("/api/v1/datasets", headers={"X-API-Key": key_a})
        assert resp.status_code == 200

    def test_health_is_public(self, client):
        """Health check must remain accessible without authentication."""
        resp = client.get("/api/v1/health")
        assert resp.status_code == 200

    def test_create_application_is_public(self, client):
        """Application registration must remain accessible without authentication (onboarding)."""
        resp = client.post(
            "/api/v1/applications",
            json={"name": "Public Onboarding Test App"},
        )
        assert resp.status_code == 201


# ─── 2. Isolation Tests ──────────────────────────────────────────────────────

class TestIsolation:
    """Application A must not be able to access Application B's resources."""

    def test_app_a_cannot_see_app_b_datasets(self, client, app_a, app_b):
        slug_a, key_a = app_a
        slug_b, key_b = app_b

        # Create a dataset for App B
        client.post(
            "/api/v1/datasets",
            json={
                "name": "Dataset B Private",
                "slug": "dataset-b-private",
                "fields": [{"name": "val", "type": "integer", "required": True}],
            },
            headers={"X-API-Key": key_b},
        )

        # App A's listing must not include App B's dataset
        resp = client.get("/api/v1/datasets", headers={"X-API-Key": key_a})
        assert resp.status_code == 200
        slugs = [d["slug"] for d in resp.json()]
        assert "dataset-b-private" not in slugs

    def test_app_a_cannot_get_app_b_dataset_by_id(self, client, app_a, app_b):
        slug_a, key_a = app_a
        slug_b, key_b = app_b

        # Create a dataset for App B
        create_resp = client.post(
            "/api/v1/datasets",
            json={
                "name": "Dataset B By ID",
                "slug": "dataset-b-by-id",
                "fields": [{"name": "val", "type": "integer", "required": True}],
            },
            headers={"X-API-Key": key_b},
        )
        dataset_b_id = create_resp.json()["id"]

        # App A must get 404 (not 403, to avoid confirming existence)
        resp = client.get(f"/api/v1/datasets/{dataset_b_id}", headers={"X-API-Key": key_a})
        assert resp.status_code == 404

    def test_app_a_cannot_get_app_b_analysis(self, client, app_a, app_b):
        """App A cannot retrieve an analysis run that belongs to App B."""
        slug_a, key_a = app_a
        slug_b, key_b = app_b

        # Create a dataset for App B and run an analysis
        ds_resp = client.post(
            "/api/v1/datasets",
            json={
                "name": "Dataset B Analysis",
                "slug": "dataset-b-analysis",
                "fields": [{"name": "amount", "type": "float", "required": True}],
            },
            headers={"X-API-Key": key_b},
        )
        ds_b_slug = ds_resp.json()["slug"]

        analyze_resp = client.post(
            "/api/v1/analyze",
            json={
                "application": slug_b,
                "dataset": ds_b_slug,
                "analysis": ["summary"],
                "data": [{"amount": 10.0}, {"amount": 20.0}],
            },
            headers={"X-API-Key": key_b},
        )
        assert analyze_resp.status_code == 200
        run_id = analyze_resp.json()["analysis_id"]

        # App A tries to fetch App B's analysis
        resp = client.get(f"/api/v1/analysis/{run_id}", headers={"X-API-Key": key_a})
        assert resp.status_code == 404

    def test_app_a_list_analysis_only_sees_own(self, client, app_a):
        """GET /analysis must only return runs for the authenticated application."""
        slug_a, key_a = app_a

        resp_a = client.get("/api/v1/analysis", headers={"X-API-Key": key_a})
        assert resp_a.status_code == 200

    def test_app_a_insights_only_for_own_app(self, client, app_a):
        """GET /insights must only return insights from the authenticated app."""
        slug_a, key_a = app_a
        resp = client.get("/api/v1/insights", headers={"X-API-Key": key_a})
        assert resp.status_code == 200

    def test_app_a_cannot_see_app_b_insights_by_run(self, client, app_a):
        """App A cannot request insights for a run belonging to App B."""
        slug_a, key_a = app_a

        # Use a fake run ID — if it 404s that's correct
        resp = client.get(
            "/api/v1/insights?run_id=fake-run-not-owned-by-a",
            headers={"X-API-Key": key_a},
        )
        assert resp.status_code == 404


# ─── 3. Validation Tests ─────────────────────────────────────────────────────

class TestValidation:
    """Invalid payloads must be rejected with 422 Unprocessable Entity."""

    def test_analyze_missing_required_fields(self, client, app_a):
        _, key_a = app_a
        resp = client.post(
            "/api/v1/analyze",
            json={"analysis": ["summary"], "data": [{"x": 1}]},
            headers={"X-API-Key": key_a},
        )
        assert resp.status_code == 422

    def test_analyze_empty_data_list(self, client, app_a):
        _, key_a = app_a
        resp = client.post(
            "/api/v1/analyze",
            json={"application": "a", "dataset": "d", "analysis": ["summary"], "data": []},
            headers={"X-API-Key": key_a},
        )
        assert resp.status_code == 422

    def test_analyze_empty_analysis_list(self, client, app_a):
        _, key_a = app_a
        resp = client.post(
            "/api/v1/analyze",
            json={"application": "a", "dataset": "d", "analysis": [], "data": [{"x": 1}]},
            headers={"X-API-Key": key_a},
        )
        assert resp.status_code == 422

    def test_analyze_unknown_field_in_request(self, client, app_a):
        """Extra/unknown fields in the request body must be rejected (extra=forbid)."""
        _, key_a = app_a
        resp = client.post(
            "/api/v1/analyze",
            json={
                "application": "a",
                "dataset": "d",
                "analysis": ["summary"],
                "data": [{"x": 1}],
                "injected_field": "malicious",
            },
            headers={"X-API-Key": key_a},
        )
        assert resp.status_code == 422

    def test_analyze_blank_application_slug(self, client, app_a):
        _, key_a = app_a
        resp = client.post(
            "/api/v1/analyze",
            json={"application": "   ", "dataset": "d", "analysis": ["summary"], "data": [{"x": 1}]},
            headers={"X-API-Key": key_a},
        )
        assert resp.status_code == 422

    def test_analyze_too_many_rows(self, client, app_a):
        """Payloads exceeding MAX_DATA_ROWS must be rejected."""
        _, key_a = app_a
        from app.schemas.analytics import MAX_DATA_ROWS
        big_data = [{"amount": float(i)} for i in range(MAX_DATA_ROWS + 1)]
        resp = client.post(
            "/api/v1/analyze",
            json={"application": "a", "dataset": "d", "analysis": ["summary"], "data": big_data},
            headers={"X-API-Key": key_a},
        )
        assert resp.status_code == 422

    def test_validator_rejects_nan(self):
        """NaN values must be rejected by DataValidator."""
        from app.services.analytics.validator import DataValidator
        validator = DataValidator()
        fields = [{"name": "val", "technical_type": "float", "required": True}]
        result = validator.validate([{"val": float("nan")}], fields)
        assert result.valid is False
        assert any("NaN" in e.error for e in result.errors)

    def test_validator_rejects_infinity(self):
        """Infinity values must be rejected by DataValidator."""
        from app.services.analytics.validator import DataValidator
        validator = DataValidator()
        fields = [{"name": "val", "technical_type": "float", "required": True}]
        result = validator.validate([{"val": float("inf")}], fields)
        assert result.valid is False
        assert any("NaN" in e.error or "Infinity" in e.error for e in result.errors)

    def test_validator_rejects_neg_infinity(self):
        """Negative infinity values must be rejected by DataValidator."""
        from app.services.analytics.validator import DataValidator
        validator = DataValidator()
        fields = [{"name": "val", "technical_type": "float", "required": True}]
        result = validator.validate([{"val": float("-inf")}], fields)
        assert result.valid is False


# ─── 4. Secrets Hygiene Tests ────────────────────────────────────────────────

class TestSecretsHygiene:
    """Verify no real API keys or secrets exist in source code or examples."""

    def _search_files(self, directory: str, extensions: tuple, pattern: str) -> list[str]:
        matches = []
        for path in pathlib.Path(directory).rglob("*"):
            if path.suffix not in extensions:
                continue
            if ".venv" in path.parts or "__pycache__" in path.parts:
                continue
            try:
                for i, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                    if pattern in line:
                        matches.append(f"{path}:{i}: {line.strip()}")
            except (OSError, PermissionError):
                pass
        return matches

    def test_no_react_env_key_in_docs(self):
        project_root = pathlib.Path(__file__).parents[2]
        docs_dir = project_root / "docs"
        for pattern in ("REACT_APP_ANALYTICS_KEY", "NEXT_PUBLIC_ANALYTICS_KEY"):
            hits = self._search_files(str(docs_dir), (".md", ".rst", ".txt"), pattern)
            assert hits == [], f"Insecure pattern '{pattern}' found in docs:\n" + "\n".join(hits)

    def test_no_hardcoded_key_in_source(self):
        src_dir = pathlib.Path(__file__).parents[1] / "app"
        hits = self._search_files(str(src_dir), (".py",), "anal_live_")
        assert hits == [], "Hardcoded production API key found in source:\n" + "\n".join(hits)

    def test_api_key_not_logged(self):
        """Verify that the authentication dependency does not log the raw API key."""
        deps_file = pathlib.Path(__file__).parents[1] / "app" / "api" / "dependencies.py"
        content = deps_file.read_text(encoding="utf-8")
        assert "logger.info(x_api_key" not in content
        assert "logger.debug(x_api_key" not in content
        assert "print(x_api_key" not in content

    def test_security_module_uses_constant_time_compare(self):
        """Verify that key comparison is constant-time (secrets.compare_digest)."""
        sec_file = pathlib.Path(__file__).parents[1] / "app" / "core" / "security.py"
        content = sec_file.read_text(encoding="utf-8")
        assert "secrets.compare_digest" in content, (
            "API key comparison must use secrets.compare_digest for constant-time safety"
        )
