"""Tests for dashboard authentication — login, JWT, and admin endpoint guards."""

from __future__ import annotations

import os

# Set test environment BEFORE any app imports
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["APP_ENV"] = "testing"
os.environ["DEBUG"] = "true"
os.environ["API_KEY_HASH_SECRET"] = "test-secret"
os.environ["DASHBOARD_ADMIN_USERNAME"] = "admin"
os.environ["DASHBOARD_ADMIN_PASSWORD"] = "test-dashboard-password"
os.environ["DASHBOARD_LOGIN_PER_MINUTE"] = "1000"

# Clear the settings cache so it picks up test env vars
from app.core.config import get_settings
get_settings.cache_clear()

import pytest
from fastapi.testclient import TestClient
from app.main import app

ADMIN = {"username": "admin", "password": "test-dashboard-password"}


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module")
def client():
    """Create a test client (lifespan seeds the admin user)."""
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def token(client):
    """Log in once per module and reuse the dashboard JWT."""
    resp = client.post("/api/v1/auth/login", json=ADMIN)
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


class TestLogin:
    """POST /auth/login — seeded admin, generic401, validation."""

    def test_login_seeded_admin_returns_token(self, client):
        resp = client.post("/api/v1/auth/login", json=ADMIN)
        assert resp.status_code == 200
        data = resp.json()
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0
        assert data["username"] == "admin"
        assert len(data["access_token"]) > 20

    def test_login_wrong_password_returns_401(self, client):
        resp = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "wrong-password"},
        )
        assert resp.status_code == 401
        assert "invalides" in resp.json()["detail"].lower()

    def test_login_unknown_user_returns_401(self, client):
        """Same401 as a wrong password — never reveals user existence."""
        resp = client.post(
            "/api/v1/auth/login",
            json={"username": "no-such-user", "password": "whatever"},
        )
        assert resp.status_code == 401
        assert "invalides" in resp.json()["detail"].lower()

    def test_login_missing_fields_returns_422(self, client):
        resp = client.post("/api/v1/auth/login", json={})
        assert resp.status_code == 422


class TestCurrentUser:
    """GET /auth/me — token validation probe."""

    def test_me_with_valid_token(self, client, token):
        resp = client.get("/api/v1/auth/me", headers=_auth(token))
        assert resp.status_code == 200
        assert resp.json()["username"] == "admin"

    def test_me_without_token_returns_401(self, client):
        assert client.get("/api/v1/auth/me").status_code == 401

    def test_me_garbage_token_returns_401(self, client):
        resp = client.get("/api/v1/auth/me", headers=_auth("not-a-jwt"))
        assert resp.status_code == 401

    def test_me_api_key_header_is_not_a_token(self, client):
        """An X-API-Key must never authenticate a dashboard route."""
        resp = client.get(
            "/api/v1/auth/me",
            headers={"X-API-Key": "anal_whatever"},
        )
        assert resp.status_code == 401


class TestAdminEndpointGuards:
    """Cross-tenant admin endpoints must require the dashboard JWT.

    Regression guard for the regenerate-key takeover hole: the guard
    must fire before any404 lookup.
    """

    def test_admin_list_requires_token(self, client):
        assert client.get("/api/v1/applications/admin/all").status_code == 401

    def test_admin_list_with_token(self, client, token):
        resp = client.get("/api/v1/applications/admin/all", headers=_auth(token))
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_admin_regenerate_key_requires_token(self, client):
        resp = client.post(
            "/api/v1/applications/admin/some-id/regenerate-key"
        )
        assert resp.status_code == 401  # guard fires before the404 lookup

    def test_admin_delete_requires_token(self, client):
        resp = client.delete("/api/v1/applications/admin/some-id")
        assert resp.status_code == 401

    def test_datasets_admin_endpoints_require_token(self, client):
        assert client.get("/api/v1/datasets/all").status_code == 401
        assert client.get("/api/v1/datasets/by-app/any-slug").status_code == 401

    def test_datasets_admin_with_token(self, client, token):
        resp = client.get("/api/v1/datasets/all", headers=_auth(token))
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
