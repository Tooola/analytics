"""Honest AI status + history pagination — ai_status & GET /analysis?skip=.

Feature: a provider failure used to be a SILENT ``ai_interpretation: null``
(worse: on POST /analyze it sank the whole run). The response now carries
``ai_status`` — ``None`` not requested, ``"ok"`` delivered, ``"error"``
requested but nothing rendered — and GET /analysis gains a ``skip`` cursor.

All additive: old consumers ignore the new field/param, defaults preserve
today's behaviour.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.services.ai.engine import AIEngine

# ─── In-memory SQLite test database (module-scoped) ─────────────────────────

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


@pytest.fixture(scope="module", autouse=True)
def _db_override():
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


# ─── Helpers ─────────────────────────────────────────────────────────────────

MONTHS = ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06"]


def _rows(values):
    return [{"mois": m, "montant": v} for m, v in zip(MONTHS, values)]


def _register(client, name="App IA Statut"):
    resp = client.post("/api/v1/applications", json={"name": name})
    assert resp.status_code == 201, resp.text
    data = resp.json()
    return data["slug"], data["api_key"]


def _create_dataset(client, api_key, name="Ventes", slug="ventes"):
    resp = client.post(
        "/api/v1/datasets",
        json={
            "name": name,
            "slug": slug,
            "fields": [
                {"name": "mois", "type": "string", "required": True},
                {"name": "montant", "type": "float", "required": True},
            ],
        },
        headers={"X-API-Key": api_key},
    )
    assert resp.status_code == 201, resp.text


@pytest.fixture
def provider_down(monkeypatch):
    """Simulate Groq/Gemini being unreachable."""

    def boom(self, context):
        raise RuntimeError("provider down")

    monkeypatch.setattr(AIEngine, "interpret", boom)


def _analyze_body(slug, include_ai):
    return {
        "application": slug,
        "dataset": "ventes",
        "analysis": ["summary", "trend"],
        "include_ai": include_ai,
        "data": _rows([12000.0, 15500.0, 14800.0, 17200.0, 16900.0, 19500.0]),
    }


def _multi_body(slug, include_ai):
    return {
        "application": slug,
        "datasets": ["ventes", "electricite"],
        "analysis": ["summary"],
        "join_key": "mois",
        "include_ai": include_ai,
        "payloads": {
            "ventes": _rows([12000.0, 15500.0, 14800.0, 17200.0, 16900.0, 19500.0]),
            "electricite": _rows([420.0, 460.0, 440.0, 470.0, 455.0, 480.0]),
        },
    }


# ─── ai_status: ok / error / None ───────────────────────────────────────────


def test_quick_ai_status_ok(client):
    resp = client.post(
        "/api/v1/analyze/quick",
        json={
            "data": [{"valeur": 1.0}, {"valeur": 2.0}, {"valeur": 3.0}],
            "analysis": ["summary"],
            "include_ai": True,
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["ai_status"] == "ok"
    assert body["ai_interpretation"] is not None


def test_quick_ai_status_none_without_ai(client):
    resp = client.post(
        "/api/v1/analyze/quick",
        json={"data": [{"valeur": 1.0}, {"valeur": 2.0}], "analysis": ["summary"]},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["ai_status"] is None
    assert body["ai_interpretation"] is None


def test_analyze_ai_status_ok(client):
    slug, key = _register(client)
    _create_dataset(client, key)
    resp = client.post(
        "/api/v1/analyze",
        json=_analyze_body(slug, include_ai=True),
        headers={"X-API-Key": key},
    )
    assert resp.status_code == 200
    assert resp.json()["ai_status"] == "ok"


def test_analyze_provider_down_reports_error_and_KEEPS_run(
    client, provider_down
):
    """Provider failure must NOT sink the run — results kept, status honest."""
    slug, key = _register(client, "App Dégradation")
    _create_dataset(client, key)
    resp = client.post(
        "/api/v1/analyze",
        json=_analyze_body(slug, include_ai=True),
        headers={"X-API-Key": key},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["success"] is True
    assert body["ai_interpretation"] is None
    assert body["ai_status"] == "error"
    assert body["results"] is not None  # statistics survived

    # The run is COMPLETED, not failed (old behaviour sank it entirely).
    detail = client.get(
        f"/api/v1/analysis/{body['analysis_id']}", headers={"X-API-Key": key}
    )
    assert detail.status_code == 200
    assert detail.json()["status"] == "completed"


def test_multi_ai_status_error_reports_and_stands(client, provider_down):
    slug, key = _register(client, "App Multi Dégradée")
    _create_dataset(client, key, "Ventes", "ventes")
    _create_dataset(client, key, "Élec", "electricite")
    resp = client.post(
        "/api/v1/analyze/multi",
        json=_multi_body(slug, include_ai=True),
        headers={"X-API-Key": key},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["success"] is True
    assert body["ai_interpretation"] is None
    assert body["ai_status"] == "error"
    assert body["synthesis"] is not None  # reasoning still delivered


def test_multi_ai_status_ok(client):
    slug, key = _register(client, "App Multi OK")
    _create_dataset(client, key, "Ventes", "ventes")
    _create_dataset(client, key, "Élec", "electricite")
    resp = client.post(
        "/api/v1/analyze/multi",
        json=_multi_body(slug, include_ai=True),
        headers={"X-API-Key": key},
    )
    assert resp.status_code == 200
    assert resp.json()["ai_status"] == "ok"


def test_multi_invalid_payload_skips_ai_status_none(client, provider_down):
    """Validation failure → AI never attempted → status None, not "error"."""
    slug, key = _register(client, "App Multi Invalide")
    _create_dataset(client, key, "Ventes", "ventes")
    _create_dataset(client, key, "Élec", "electricite")
    body = _multi_body(slug, include_ai=True)
    body["payloads"]["ventes"] = [{"mois": "2026-01", "montant": "pas-un-nombre"}]
    resp = client.post(
        "/api/v1/analyze/multi", json=body, headers={"X-API-Key": key}
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["success"] is False
    assert resp.json()["ai_status"] is None


# ─── GET /analysis pagination (skip) ────────────────────────────────────────


def test_analysis_list_paginates_with_skip(client):
    slug, key = _register(client, "App Paginée")
    _create_dataset(client, key)
    headers = {"X-API-Key": key}

    ids = set()
    for _ in range(3):
        resp = client.post(
            "/api/v1/analyze",
            json=_analyze_body(slug, include_ai=False),
            headers=headers,
        )
        assert resp.status_code == 200
        ids.add(resp.json()["analysis_id"])
    assert len(ids) == 3

    page0 = client.get("/api/v1/analysis?limit=1&skip=0", headers=headers)
    page1 = client.get("/api/v1/analysis?limit=1&skip=1", headers=headers)
    assert page0.status_code == 200 and page1.status_code == 200

    run0 = page0.json()
    run1 = page1.json()
    assert len(run0) == 1 and len(run1) == 1
    assert run0[0]["id"] != run1[0]["id"]
    assert {run0[0]["id"], run1[0]["id"]} <= ids

    # End of the list → empty page, not an error.
    past_end = client.get("/api/v1/analysis?limit=1&skip=50", headers=headers)
    assert past_end.status_code == 200
    assert past_end.json() == []

    # Default call (no skip) unchanged: newest first, still valid runs.
    default = client.get("/api/v1/analysis", headers=headers)
    assert default.status_code == 200
    assert len(default.json()) >= 3

    # Negative skip rejected by validation (422).
    bad = client.get("/api/v1/analysis?skip=-1", headers=headers)
    assert bad.status_code == 422
