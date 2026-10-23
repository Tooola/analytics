"""Pytest configuration and shared fixtures."""

from __future__ import annotations

import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set test environment before importing app modules
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["APP_ENV"] = "testing"
os.environ["DEBUG"] = "true"
os.environ["API_KEY_HASH_SECRET"] = "test-secret"
# Seeded dashboard admin (login tests) — never a production value
os.environ["DASHBOARD_ADMIN_USERNAME"] = "admin"
os.environ["DASHBOARD_ADMIN_PASSWORD"] = "test-dashboard-password"
os.environ["DASHBOARD_LOGIN_PER_MINUTE"] = "1000"
# Consolidated /analyze/multi route tests fire many calls in one minute
os.environ["ANALYZE_MULTI_PER_MINUTE"] = "1000"
# Registration fixtures (apps + datasets) across the whole suite — same
# minute, same limiter bucket. POST /analyze stays 20/min: a test asserts 429.
os.environ["APPLICATIONS_CREATE_PER_MINUTE"] = "1000"
os.environ["DATASETS_CREATE_PER_MINUTE"] = "1000"
# Route tests must never reach a real provider (local .env may set groq)
os.environ["AI_PROVIDER"] = "mock"

from app.core.database import Base

# Create a test engine
test_engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create all tables once per test session."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
