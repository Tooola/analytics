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

