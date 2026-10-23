"""Business-context injection tests — the AI must receive the tenant's words.

Feature: `business_context` of the AnalyticalContext was never populated, so
providers fell back to a generic line. It is now assembled per request from
data tenants ALREADY provide (application description, dataset descriptions,
column units/semantic types) — no new required input, no global context.

engine.py is read-only: injection goes through `context.model_copy`.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.schemas.ai import AIInterpretation
from app.services.ai.business_context import build_business_context
from app.services.ai.engine import AIEngine

# ─── In-memory SQLite test database (module-scoped, like test_multi_analyze) ─

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


def _register(client, name, description=None):
    body: dict = {"name": name}
    if description:
        body["description"] = description
    resp = client.post("/api/v1/applications", json=body)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    return data["slug"], data["api_key"]


def _create_dataset(client, api_key, name, slug, fields, description=None):
    body: dict = {"name": name, "slug": slug, "fields": fields}
    if description:
        body["description"] = description
    resp = client.post(
        "/api/v1/datasets",
        json=body,
        headers={"X-API-Key": api_key},
    )
    assert resp.status_code == 201, resp.text


@pytest.fixture
def capture_context(monkeypatch):
    """Monkeypatch AIEngine.interpret to capture the context it receives."""
    captured: list = []

    def fake_interpret(self, context):
        captured.append(context)
        return AIInterpretation(provider="mock-capture", summary="test")

    monkeypatch.setattr(AIEngine, "interpret", fake_interpret)
    return captured


# ─── Unit: build_business_context ────────────────────────────────────────────


def test_unit_full_context_includes_descriptions_units_semantics():
    text = build_business_context(
        "Farmtinz",
        "Suivi agricole multi-parcelles",
        [
            {
                "name": "Ventes terrain",
                "slug": "ventes-terrain",
                "description": "Ventes mensuelles par parcelle",
                "fields": [
                    {
                        "name": "montant",
                        "unit": "€",
                        "semantic_type": "quantity",
                        "description": "Montant TTC",
                    },
                    {"name": "mois", "unit": None, "semantic_type": None, "description": None},
                ],
            }
        ],
    )
    assert "Farmtinz" in text
    assert "Suivi agricole multi-parcelles" in text
    assert "Ventes terrain" in text
    assert "Ventes mensuelles par parcelle" in text
    assert "unité : €" in text
    assert "quantity" in text


def test_unit_no_descriptions_degrades_gracefully():
    text = build_business_context(
        "App nue", None,
        [{"name": None, "slug": "s1", "description": None, "fields": []}],
    )
    assert "App nue" in text
    assert "s1" in text  # slug used when name missing


def test_unit_long_descriptions_are_capped():
    text = build_business_context(
        "App", "x" * 5000,
        [{"name": "d", "slug": "d", "description": "y" * 5000, "fields": []}],
    )
    assert len(text) <= 3000


# ─── Integration: /analyze ───────────────────────────────────────────────────


def test_analyze_ai_receives_app_and_dataset_context(client, capture_context):
    slug, key = _register(
        client, "Maison Energie", "Pilotage énergétique de bâtiments tertiaires"
    )
    _create_dataset(
        client, key, "Factures", "factures",
        [
            {"name": "mois", "type": "string", "required": True},
            {"name": "montant", "type": "float", "required": True, "unit": "€"},
        ],
        description="Factures mensuelles d'électricité",
    )
    resp = client.post(
        "/api/v1/analyze",
        json={
            "application": slug,
            "dataset": "factures",
            "analysis": ["summary", "trend"],
            "include_ai": True,
            "data": _rows([420.0, 460.0, 440.0, 470.0, 455.0, 480.0]),
        },
        headers={"X-API-Key": key},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["ai_interpretation"] is not None

    assert len(capture_context) == 1
    bc = capture_context[0].business_context
    assert bc is not None
    assert "Maison Energie" in bc
    assert "Pilotage énergétique" in bc
    assert "Factures mensuelles" in bc
    assert "unité : €" in bc


def test_analyze_without_ai_keeps_null_and_skips_context(client, capture_context):
    slug, key = _register(client, "App Sans IA")
    _create_dataset(client, key, "Ventes", "ventes", [
        {"name": "mois", "type": "string", "required": True},
        {"name": "montant", "type": "float", "required": True},
    ])
    resp = client.post(
        "/api/v1/analyze",
        json={
            "application": slug,
            "dataset": "ventes",
            "analysis": ["summary"],
            "data": _rows([1.0, 2.0, 3.0, 4.0, 5.0, 6.0]),
        },
        headers={"X-API-Key": key},
    )
    assert resp.status_code == 200
    assert resp.json()["ai_interpretation"] is None
    assert capture_context == []  # provider never called


# ─── Integration: /analyze/multi ─────────────────────────────────────────────


def test_multi_ai_receives_every_dataset_context(client, capture_context):
    slug, key = _register(
        client, "Structure Financière", "Consolidation budget départements"
    )
    _create_dataset(client, key, "Ventes", "ventes-terrain", [
        {"name": "mois", "type": "string", "required": True},
        {"name": "montant", "type": "float", "required": True, "unit": "€"},
    ])
    _create_dataset(client, key, "Élec", "electricite", [
        {"name": "mois", "type": "string", "required": True},
        {"name": "montant", "type": "float", "required": True, "unit": "€"},
    ])
    resp = client.post(
        "/api/v1/analyze/multi",
        json={
            "application": slug,
            "datasets": ["ventes-terrain", "electricite"],
            "analysis": ["summary", "trend"],
            "join_key": "mois",
            "include_ai": True,
            "payloads": {
                "ventes-terrain": _rows([12000.0, 15500.0, 14800.0, 17200.0, 16900.0, 19500.0]),
                "electricite": _rows([420.0, 460.0, 440.0, 470.0, 455.0, 480.0]),
            },
        },
        headers={"X-API-Key": key},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["ai_interpretation"] is not None

    bc = capture_context[0].business_context
    assert "Structure Financière" in bc
    assert "Consolidation budget" in bc
    assert "ventes-terrain" in bc
    assert "electricite" in bc


# ─── Integration: /analyze/quick (sandbox) ───────────────────────────────────


def test_quick_labels_itself_as_sandbox(client, capture_context):
    resp = client.post(
        "/api/v1/analyze/quick",
        json={
            "data": [{"valeur": 1.0}, {"valeur": 2.0}, {"valeur": 3.0}],
            "analysis": ["summary"],
            "include_ai": True,
            "label": "essai-marche",
        },
    )
    assert resp.status_code == 200, resp.text
    bc = capture_context[0].business_context
    assert "Banc d'essai" in bc
    assert "essai-marche" in bc
