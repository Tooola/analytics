"""Tests for API endpoints — lightweight tests that don't require database."""

from __future__ import annotations

import os

# Set test environment BEFORE any app imports
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["APP_ENV"] = "testing"
os.environ["DEBUG"] = "true"
os.environ["API_KEY_HASH_SECRET"] = "test-secret"

# Clear the settings cache so it picks up test env vars
from app.core.config import get_settings
get_settings.cache_clear()

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module")
def client():
    """Create a test client."""
    with TestClient(app) as c:
        yield c


class TestRootEndpoint:
    """Tests for GET /"""

    def test_root_returns_info(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert data["version"] == "1.0.0"


class TestDocsEndpoint:
    """Tests for API documentation endpoints."""

    def test_docs_available(self, client):
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_schema(self, client):
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "paths" in schema
        assert "/api/v1/health" in schema["paths"]
        assert "/api/v1/applications" in schema["paths"]
        assert "/api/v1/datasets" in schema["paths"]
        assert "/api/v1/analyze" in schema["paths"]


class TestSecurityUtils:
    """Tests for API key security utilities."""

    def test_generate_api_key_prefix(self):
        from app.core.security import generate_api_key
        from app.core.config import settings
        key = generate_api_key()
        assert key.startswith(settings.api_key_prefix)


class TestTimestampSerialisation:
    """PLAN.md S2: every API timestamp is aware UTC (+00:00), like /health."""

    @staticmethod
    def _read(created_at):
        from app.models import ApplicationStatus
        from app.schemas.application import ApplicationRead

        return ApplicationRead(
            id="x", name="n", slug="s", description=None,
            status=ApplicationStatus.active,
            created_at=created_at, updated_at=created_at,
        )

    def test_naive_datetime_serialised_as_utc(self):
        from datetime import datetime

        read = self._read(datetime(2026, 1, 2, 3, 4, 5))
        assert read.created_at.tzinfo is not None
        assert read.created_at.utcoffset().total_seconds() == 0
        # Pydantic serialises UTC with the ISO 'Z' designator.
        assert '"created_at":"2026-01-02T03:04:05Z"' in read.model_dump_json()

    def test_aware_datetime_converted_to_utc(self):
        from datetime import datetime, timedelta, timezone

        aware = datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone(timedelta(hours=2)))
        read = self._read(aware)
        assert read.created_at.utcoffset() == timedelta(0)
        assert read.created_at.hour == 1  # 03:04 at +02:00 → 01:04 UTC

    def test_health_timestamp_uses_same_utc_designator(self, client):
        resp = client.get("/api/v1/health")
        assert resp.status_code == 200
        assert resp.json()["timestamp"].endswith("Z")

