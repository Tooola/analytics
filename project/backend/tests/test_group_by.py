"""Segment analysis — group_by (analyse par segment).

Feature: every service only looked at NUMERIC columns — a categorical
dimension (produit, région…) sent by the application was simply ignored.
``group_by`` cuts all numeric measures by ONE categorical column: *which
segment carries the number?*

All additive: without ``group_by`` today's responses are unchanged (quick:
no ``grouped`` key at all; typed responses: ``grouped: null``).
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
from app.services.ai.engine import AIEngine
from app.services.analytics.grouped import build_grouped, grouped_context_line

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

# Riz 600 · Blé 400 · Maïs 200 — total 1200 (ranking + shares are exact).
ROWS = [
    {"mois": "2026-01", "montant": 100.0, "produit": "Riz"},
    {"mois": "2026-02", "montant": 200.0, "produit": "Riz"},
    {"mois": "2026-03", "montant": 300.0, "produit": "Riz"},
    {"mois": "2026-04", "montant": 50.0, "produit": "Maïs"},
    {"mois": "2026-05", "montant": 150.0, "produit": "Maïs"},
    {"mois": "2026-06", "montant": 400.0, "produit": "Blé"},
]

FIELDS = [
    {"name": "mois", "technical_type": "string"},
    {"name": "montant", "technical_type": "float"},
    {"name": "produit", "technical_type": "string"},
]

ELEC_ROWS = [
    {"mois": "2026-01", "montant": 420.0},
    {"mois": "2026-02", "montant": 460.0},
    {"mois": "2026-03", "montant": 440.0},
    {"mois": "2026-04", "montant": 470.0},
    {"mois": "2026-05", "montant": 455.0},
    {"mois": "2026-06", "montant": 480.0},
]


def _register(client, name):
    resp = client.post("/api/v1/applications", json={"name": name})
    assert resp.status_code == 201, resp.text
    data = resp.json()
    return data["slug"], data["api_key"]


def _create_dataset(client, api_key, name, slug, with_produit=True):
    fields = [
        {"name": "mois", "type": "string", "required": True},
        {"name": "montant", "type": "float", "required": True},
    ]
    if with_produit:
        fields.append({"name": "produit", "type": "string", "required": False})
    resp = client.post(
        "/api/v1/datasets",
        json={"name": name, "slug": slug, "fields": fields},
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


# ─── Unit: build_grouped ────────────────────────────────────────────────────


def test_grouped_service_cuts_orders_and_shares():
    grouped = build_grouped(ROWS, FIELDS, "produit")

    assert grouped["group_by"] == "produit"
    assert grouped["ranked_by"] == "montant"
    assert grouped["segment_count"] == 3
    assert grouped["note"] is None

    # Descending by segment total of the ranking metric: Riz 600 > Blé 400 > Maïs 200.
    segments = grouped["segments"]
    assert [s["segment"] for s in segments] == ["Riz", "Blé", "Maïs"]
    assert [s["rank"] for s in segments] == [1, 2, 3]
    assert [s["row_count"] for s in segments] == [3, 1, 2]

    riz = segments[0]["metrics"]["montant"]
    assert riz["count"] == 3
    assert riz["sum"] == 600.0
    assert riz["mean"] == 200.0
    assert riz["share"] == 0.5  # 600 / 1200 — shares sum to ~1 per metric

    ble = segments[1]["metrics"]["montant"]
    assert ble["count"] == 1
    assert ble["std"] == 0.0  # single value → no dispersion

    # The dimension is never its own measure.
    assert "produit" not in segments[0]["metrics"]


def test_grouped_service_missing_column_soft_fails():
    grouped = build_grouped(ROWS, FIELDS, "region")
    assert grouped["segments"] == []
    assert grouped["segment_count"] == 0
    assert "absente" in grouped["note"]


def test_grouped_service_no_numeric_measure():
    string_only = [{"produit": "Riz"}, {"produit": "Maïs"}]
    fields = [{"name": "produit", "technical_type": "string"}]
    grouped = build_grouped(string_only, fields, "produit")
    assert grouped["segments"] == []
    assert "aucune colonne numérique" in grouped["note"]


def test_grouped_service_numeric_dimension_not_its_own_measure():
    rows = [
        {"zone_id": 1, "montant": 10.0},
        {"zone_id": 1, "montant": 30.0},
        {"zone_id": 2, "montant": 50.0},
    ]
    fields = [
        {"name": "zone_id", "technical_type": "integer"},
        {"name": "montant", "technical_type": "float"},
    ]
    grouped = build_grouped(rows, fields, "zone_id")
    # The dimension is never its own measure → ranking falls on montant.
    assert grouped["ranked_by"] == "montant"
    metrics = grouped["segments"][0]["metrics"]
    assert set(metrics) == {"montant"}  # zone_id excluded even though numeric


def test_grouped_service_caps_cardinality_with_note():
    rows = [{"produit": f"s{i:02d}", "montant": 1.0} for i in range(60)]
    fields = [
        {"name": "produit", "technical_type": "string"},
        {"name": "montant", "technical_type": "float"},
    ]
    grouped = build_grouped(rows, fields, "produit")
    assert grouped["segment_count"] == 60
    assert len(grouped["segments"]) == 50  # capped, never streamed blindly
    assert "50 premiers" in grouped["note"]


def test_grouped_service_share_none_when_total_zero():
    rows = [
        {"produit": "A", "montant": 10.0},
        {"produit": "A", "montant": -10.0},
        {"produit": "B", "montant": 5.0},
        {"produit": "B", "montant": -5.0},
    ]
    fields = [
        {"name": "produit", "technical_type": "string"},
        {"name": "montant", "technical_type": "float"},
    ]
    grouped = build_grouped(rows, fields, "produit")
    assert grouped["segments"]
    for seg in grouped["segments"]:
        assert seg["metrics"]["montant"]["share"] is None


def test_grouped_context_line_compact_and_capped():
    assert grouped_context_line(None) == ""

    empty = {
        "group_by": "region",
        "ranked_by": None,
        "segment_count": 0,
        "segments": [],
        "note": "colonne « region » absente des données",
    }
    assert "absente" in grouped_context_line(empty)

    grouped = build_grouped(ROWS, FIELDS, "produit")
    line = grouped_context_line(grouped)
    assert "Analyse par segment « produit »" in line
    assert "Riz 50.0%" in line
    assert "33.3%" in line  # Blé 400/1200
    assert "3 segment(s)" in line
    assert "…" not in line  # 3 ≤ 5 rendered → no ellipsis

    big_rows = [
        {"produit": f"s{i:02d}", "montant": float(i + 1)} for i in range(7)
    ]
    big_fields = [
        {"name": "produit", "technical_type": "string"},
        {"name": "montant", "technical_type": "float"},
    ]
    big_line = grouped_context_line(build_grouped(big_rows, big_fields, "produit"))
    assert "…" in big_line
    assert "7 segment(s)" in big_line


# ─── Quick endpoint ─────────────────────────────────────────────────────────


def test_quick_group_by_returns_grouped(client):
    resp = client.post(
        "/api/v1/analyze/quick",
        json={"data": ROWS, "analysis": ["summary"], "group_by": "produit"},
    )
    assert resp.status_code == 200, resp.text
    grouped = resp.json()["results"]["grouped"]
    assert grouped["group_by"] == "produit"
    assert [s["segment"] for s in grouped["segments"]] == ["Riz", "Blé", "Maïs"]


def test_quick_without_group_by_has_no_grouped_key(client):
    """Zero incidence: today's quick payload keeps exactly its shape."""
    resp = client.post(
        "/api/v1/analyze/quick",
        json={"data": ROWS, "analysis": ["summary"]},
    )
    assert resp.status_code == 200
    assert "grouped" not in resp.json()["results"]


# ─── /analyze ───────────────────────────────────────────────────────────────


def test_analyze_group_by_typed_and_persisted(client):
    slug, key = _register(client, "App Segments")
    _create_dataset(client, key, "Ventes", "ventes")
    resp = client.post(
        "/api/v1/analyze",
        json={
            "application": slug,
            "dataset": "ventes",
            "analysis": ["summary"],
            "group_by": "produit",
            "data": ROWS,
        },
        headers={"X-API-Key": key},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["success"] is True

    grouped = body["results"]["grouped"]
    assert grouped["group_by"] == "produit"
    assert grouped["ranked_by"] == "montant"
    assert len(grouped["segments"]) == 3
    assert grouped["segments"][0]["segment"] == "Riz"
    assert grouped["segments"][0]["metrics"]["montant"]["share"] == 0.5

    # Persisted with the run — the detail endpoint carries it back.
    detail = client.get(
        f"/api/v1/analysis/{body['analysis_id']}", headers={"X-API-Key": key}
    )
    assert detail.status_code == 200
    assert detail.json()["results"]["grouped"]["group_by"] == "produit"


def test_analyze_without_group_by_grouped_null(client):
    slug, key = _register(client, "App Sans Segment")
    _create_dataset(client, key, "Ventes", "ventes")
    resp = client.post(
        "/api/v1/analyze",
        json={
            "application": slug,
            "dataset": "ventes",
            "analysis": ["summary"],
            "data": ROWS,
        },
        headers={"X-API-Key": key},
    )
    assert resp.status_code == 200
    assert resp.json()["results"]["grouped"] is None


def test_analyze_group_by_unknown_column_soft_fails(client):
    """Wrong column: the analysis still completes, grouped explains why."""
    slug, key = _register(client, "App Mauvaise Colonne")
    _create_dataset(client, key, "Ventes", "ventes")
    resp = client.post(
        "/api/v1/analyze",
        json={
            "application": slug,
            "dataset": "ventes",
            "analysis": ["summary"],
            "group_by": "region",
            "data": ROWS,
        },
        headers={"X-API-Key": key},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["results"]["summary"] is not None  # statistics survived
    grouped = body["results"]["grouped"]
    assert grouped["segments"] == []
    assert "absente" in grouped["note"]

    # The run is COMPLETED (soft-fail contract), not failed.
    detail = client.get(
        f"/api/v1/analysis/{body['analysis_id']}", headers={"X-API-Key": key}
    )
    assert detail.json()["status"] == "completed"


def test_analyze_group_by_too_long_422(client):
    slug, key = _register(client, "App Colonne Longue")
    _create_dataset(client, key, "Ventes", "ventes")
    resp = client.post(
        "/api/v1/analyze",
        json={
            "application": slug,
            "dataset": "ventes",
            "analysis": ["summary"],
            "group_by": "x" * 256,
            "data": ROWS,
        },
        headers={"X-API-Key": key},
    )
    assert resp.status_code == 422


# ─── /analyze/multi ─────────────────────────────────────────────────────────


def test_multi_group_by_only_where_column_exists(client):
    slug, key = _register(client, "App Multi Segments")
    _create_dataset(client, key, "Ventes", "ventes", with_produit=True)
    _create_dataset(client, key, "Élec", "electricite", with_produit=False)
    resp = client.post(
        "/api/v1/analyze/multi",
        json={
            "application": slug,
            "datasets": ["ventes", "electricite"],
            "analysis": ["summary"],
            "join_key": "mois",
            "group_by": "produit",
            "payloads": {"ventes": ROWS, "electricite": ELEC_ROWS},
        },
        headers={"X-API-Key": key},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["success"] is True

    ventes = body["results"]["ventes"]["grouped"]
    assert len(ventes["segments"]) == 3
    assert ventes["segments"][0]["segment"] == "Riz"

    # No "produit" column here — an EMPTY grouped with the reason, not silence.
    elec = body["results"]["electricite"]["grouped"]
    assert elec["segments"] == []
    assert "absente" in elec["note"]


def test_multi_without_group_by_grouped_null_everywhere(client):
    slug, key = _register(client, "App Multi Sans Segment")
    _create_dataset(client, key, "Ventes", "ventes", with_produit=True)
    _create_dataset(client, key, "Élec", "electricite", with_produit=False)
    resp = client.post(
        "/api/v1/analyze/multi",
        json={
            "application": slug,
            "datasets": ["ventes", "electricite"],
            "analysis": ["summary"],
            "join_key": "mois",
            "payloads": {"ventes": ROWS, "electricite": ELEC_ROWS},
        },
        headers={"X-API-Key": key},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["results"]["ventes"]["grouped"] is None
    assert body["results"]["electricite"]["grouped"] is None


# ─── AI receives the segment line ───────────────────────────────────────────


def test_ai_receives_segment_line_in_business_context(client, capture_context):
    slug, key = _register(client, "App IA Segments")
    _create_dataset(client, key, "Ventes", "ventes")
    resp = client.post(
        "/api/v1/analyze",
        json={
            "application": slug,
            "dataset": "ventes",
            "analysis": ["summary"],
            "group_by": "produit",
            "include_ai": True,
            "data": ROWS,
        },
        headers={"X-API-Key": key},
    )
    assert resp.status_code == 200
    assert resp.json()["ai_status"] == "ok"

    assert len(capture_context) == 1
    bc = capture_context[0].business_context
    assert "Analyse par segment « produit »" in bc
    assert "Riz 50.0%" in bc
    assert "App IA Segments" in bc  # BLOC 1 context still there
