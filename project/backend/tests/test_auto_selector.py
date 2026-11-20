"""Tests for auto_selector — intelligent auto-selection of analyses."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.analytics.auto_selector import auto_select_analyses


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_auto_selector_empty_data():
    assert auto_select_analyses([], []) == ["summary"]


def test_auto_selector_small_data():
    data = [{"x": 1}, {"x": 2}]
    fields = [{"name": "x", "technical_type": "integer"}]
    # Less than 3 rows -> summary only
    assert auto_select_analyses(data, fields) == ["summary"]


def test_auto_selector_time_series():
    data = [
        {"date": f"2026-01-0{i}", "ventes": 100 + i * 10, "visiteurs": 1000 + i * 50}
        for i in range(1, 9)
    ]
    fields = [
        {"name": "date", "technical_type": "date"},
        {"name": "ventes", "technical_type": "integer"},
        {"name": "visiteurs", "technical_type": "integer"},
    ]
    selected = auto_select_analyses(data, fields)
    assert "summary" in selected
    assert "trend" in selected
    assert "forecast" in selected
    assert "anomaly" in selected
    assert "correlation" in selected


def test_auto_selector_demographic_no_dates():
    data = [
        {"region": "R1", "population": 1000, "chomage": 5.5, "revenu": 25000},
        {"region": "R2", "population": 2000, "chomage": 6.5, "revenu": 23000},
        {"region": "R3", "population": 1500, "chomage": 7.0, "revenu": 21000},
        {"region": "R4", "population": 3000, "chomage": 4.5, "revenu": 31000},
        {"region": "R5", "population": 2500, "chomage": 8.0, "revenu": 20000},
        {"region": "R6", "population": 1800, "chomage": 5.0, "revenu": 27000},
    ]
    fields = [
        {"name": "region", "technical_type": "string"},
        {"name": "population", "technical_type": "integer"},
        {"name": "chomage", "technical_type": "float"},
        {"name": "revenu", "technical_type": "integer"},
    ]
    selected = auto_select_analyses(data, fields)
    assert "summary" in selected
    assert "anomaly" in selected
    assert "correlation" in selected
    assert "trend" not in selected
    assert "forecast" not in selected


def test_quick_analyze_with_auto(client):
    resp = client.post(
        "/api/v1/analyze/quick",
        json={
            "data": [
                {"date": "2026-01-01", "score": 10},
                {"date": "2026-01-02", "score": 20},
                {"date": "2026-01-03", "score": 30},
                {"date": "2026-01-04", "score": 40},
                {"date": "2026-01-05", "score": 50},
                {"date": "2026-01-06", "score": 60},
            ],
            "analysis": ["auto"],
            "include_ai": False,
        },
    )
    assert resp.status_code == 200
    res = resp.json()["results"]
    assert "summary" in res
    assert "trend" in res
