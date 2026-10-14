"""Consolidated multi-dataset analysis tests — POST /analyze/multi.

The core product story: a structure with several departments/sources gets
analysed in ONE pass — per-dataset results, links BETWEEN datasets, and a
decision-oriented synthesis — plus the guard rails (auth, tenant isolation,
payload/dataset matching, dataset cap).
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db

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


@pytest.fixture(scope="module", autouse=True)
def _db_override():
    """Scope the get_db override to THIS module only (global state)."""
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


# ─── Fixtures ────────────────────────────────────────────────────────────────

MONTHS = ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06"]
VENTES = [100.0, 150.0, 200.0, 250.0, 300.0, 350.0]
SURFACE = [900.0, 850.0, 800.0, 750.0, 700.0, 650.0]
ELEC = [v * 2 for v in VENTES]  # perfectly correlated with ventes


def _ventes_rows():
    return [
        {"mois": m, "montant_vente": v, "surface": s}
        for m, v, s in zip(MONTHS, VENTES, SURFACE)
    ]


def _elec_rows():
    # kwh is constant → pearson is undefined → must NOT appear in links.
    return [{"mois": m, "montant_elec": e, "kwh": 100.0} for m, e in zip(MONTHS, ELEC)]


def _register(client, name):
    resp = client.post("/api/v1/applications", json={"name": name})
    assert resp.status_code == 201, resp.text
    data = resp.json()
    return data["slug"], data["api_key"]


def _create_dataset(client, api_key, name, slug, fields):
    resp = client.post(
        "/api/v1/datasets",
        json={"name": name, "slug": slug, "fields": fields},
        headers={"X-API-Key": api_key},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


@pytest.fixture(scope="module")
def org(client):
    """Multi-department structure: one app, two datasets (terrain + élec)."""
    slug, key = _register(client, "Structure Multi Dept")
    _create_dataset(client, key, "Ventes terrain", "ventes-terrain", [
        {"name": "mois", "type": "string", "required": True},
        {"name": "montant_vente", "type": "float", "required": True},
        {"name": "surface", "type": "float", "required": True},
    ])
    _create_dataset(client, key, "Electricite", "electricite", [
        {"name": "mois", "type": "string", "required": True},
        {"name": "montant_elec", "type": "float", "required": True},
        {"name": "kwh", "type": "float", "required": True},
    ])
    return {"slug": slug, "key": key, "headers": {"X-API-Key": key}}


@pytest.fixture(scope="module")
def outsider(client):
    """Another tenant — its datasets must stay invisible to `org`."""
    slug, key = _register(client, "Structure Autre")
    _create_dataset(client, key, "Dept Autre", "dept-inconnu", [
        {"name": "mois", "type": "string", "required": True},
    ])
    return {"slug": slug, "key": key, "headers": {"X-API-Key": key}}


def _multi_body(org, **overrides):
    body = {
        "application": org["slug"],
        "datasets": ["ventes-terrain", "electricite"],
        "analysis": ["summary", "trend", "anomaly"],
        "payloads": {
            "ventes-terrain": _ventes_rows(),
            "electricite": _elec_rows(),
        },
        "join_key": "mois",
        "include_ai": False,
    }
    body.update(overrides)
    return body


# ─── Authentication & isolation ──────────────────────────────────────────────


class TestMultiAnalyzeGuards:

    def test_requires_api_key(self, client, org):
        resp = client.post("/api/v1/analyze/multi", json=_multi_body(org))
        assert resp.status_code == 401

    def test_api_key_must_match_application(self, client, org, outsider):
        """Another tenant's key cannot run against this application."""
        resp = client.post(
            "/api/v1/analyze/multi",
            json=_multi_body(org),
            headers=outsider["headers"],
        )
        assert resp.status_code == 403

    def test_unknown_dataset_is_404(self, client, org):
        body = _multi_body(
            org,
            datasets=["ventes-terrain", "ghost-ds"],
            payloads={"ventes-terrain": _ventes_rows(), "ghost-ds": _elec_rows()},
        )
        resp = client.post("/api/v1/analyze/multi", json=body, headers=org["headers"])
        assert resp.status_code == 404

    def test_cross_tenant_dataset_is_404(self, client, org, outsider):
        """A slug owned by another tenant is 'not found' for this app."""
        body = _multi_body(
            org,
            datasets=["dept-inconnu"],
            payloads={"dept-inconnu": _ventes_rows()},
        )
        resp = client.post("/api/v1/analyze/multi", json=body, headers=org["headers"])
        assert resp.status_code == 404

    def test_payload_key_mismatch_is_422(self, client, org):
        body = _multi_body(org)
        del body["payloads"]["electricite"]
        resp = client.post("/api/v1/analyze/multi", json=body, headers=org["headers"])
        assert resp.status_code == 422

    def test_dataset_cap_is_422(self, client, org):
        slugs = [f"ds-{i}" for i in range(11)]  # max is 10
        body = _multi_body(
            org,
            datasets=slugs,
            payloads={s: _ventes_rows() for s in slugs},
        )
        resp = client.post("/api/v1/analyze/multi", json=body, headers=org["headers"])
        assert resp.status_code == 422

    def test_duplicate_dataset_rejected(self, client, org):
        body = _multi_body(org, datasets=["ventes-terrain", "ventes-terrain"])
        resp = client.post("/api/v1/analyze/multi", json=body, headers=org["headers"])
        assert resp.status_code == 422


# ─── The consolidated pass ───────────────────────────────────────────────────


class TestMultiAnalyzeConsolidated:

    def test_one_pass_links_and_decides(self, client, org):
        """N datasets → one request: results + cross links + synthesis + AI."""
        body = _multi_body(org, include_ai=True)
        resp = client.post("/api/v1/analyze/multi", json=body, headers=org["headers"])
        assert resp.status_code == 200, resp.text
        data = resp.json()

        # Per-dataset layer: every dataset validated, analysed, persisted.
        assert data["success"] is True
        assert set(data["results"]) == {"ventes-terrain", "electricite"}
        assert set(data["analysis_ids"]) == {"ventes-terrain", "electricite"}
        assert all(v["valid"] for v in data["validations"].values())
        assert data["insights"]["ventes-terrain"]
        assert data["insights"]["electricite"]
        assert data["results"]["ventes-terrain"]["trend"][0]["direction"] == "up"

        # Cross layer: montant_vente × montant_elec move together (r = 1.0).
        links = data["cross_correlations"]
        assert links, "expected cross-dataset links"
        best = links[0]
        assert {best["dataset1"], best["dataset2"]} == {"ventes-terrain", "electricite"}
        assert abs(best["coefficient"]) >= 0.99
        assert best["strength"] == "strong"
        assert best["relationship"] == "positive"
        # surface moves the other way (r = -1.0) — negative link present too.
        assert any(
            l["column1"] == "surface" and l["relationship"] == "negative"
            for l in links
        )
        # Constant column (kwh) must never produce a link.
        assert not any("kwh" in (l["column1"], l["column2"]) for l in links)

        # Synthesis: decision block over the whole picture.
        syn = data["synthesis"]
        assert syn["datasets_analyzed"] == 2
        assert syn["total_rows"] == 12
        assert syn["join_key"] == "mois"
        assert syn["trends"] == {"ventes-terrain": "up", "electricite": "up"}
        assert syn["divergent"] is False
        assert syn["verdict"] == "positif"
        assert "Verdict" in syn["summary"]

        # AI read everything at once (mock provider in the test env).
        assert data["ai_interpretation"]

    def test_divergent_trends_flagged(self, client, org):
        """Datasets moving in opposite ways → divergent + tension verdict."""
        down_rows = [
            {"mois": m, "montant_elec": v, "kwh": 100.0}
            for m, v in zip(MONTHS, [350.0, 300.0, 250.0, 200.0, 150.0, 100.0])
        ]
        body = _multi_body(org, payloads={"ventes-terrain": _ventes_rows(), "electricite": down_rows})
        resp = client.post("/api/v1/analyze/multi", json=body, headers=org["headers"])
        assert resp.status_code == 200, resp.text
        syn = resp.json()["synthesis"]
        assert syn["trends"]["ventes-terrain"] == "up"
        assert syn["trends"]["electricite"] == "down"
        assert syn["divergent"] is True
        assert syn["verdict"] == "tension"

    def test_without_join_key_analyses_but_skips_links(self, client, org):
        body = _multi_body(org, join_key=None)
        resp = client.post("/api/v1/analyze/multi", json=body, headers=org["headers"])
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["success"] is True
        assert set(data["results"]) == {"ventes-terrain", "electricite"}
        assert data["cross_correlations"] == []
        assert data["synthesis"] is not None
        assert data["synthesis"]["join_key"] is None
        assert "join_key" in data["synthesis"]["summary"]

    def test_invalid_payload_fails_only_that_dataset(self, client, org):
        """One bad payload → its run fails, the other dataset still reports."""
        body = _multi_body(
            org,
            payloads={
                "ventes-terrain": [{"mois": "2026-01"}],  # required fields missing
                "electricite": _elec_rows(),
            },
        )
        resp = client.post("/api/v1/analyze/multi", json=body, headers=org["headers"])
        assert resp.status_code == 200, resp.text
        data = resp.json()

        assert data["success"] is False
        assert data["validations"]["ventes-terrain"]["valid"] is False
        assert "ventes-terrain" not in data["results"]
        assert "electricite" in data["results"]
        # Consolidated layer is withheld while any dataset is invalid.
        assert data["cross_correlations"] == []
        assert data["synthesis"] is None
        # The failed run is still recorded for history.
        assert "ventes-terrain" in data["analysis_ids"]

    def test_single_endpoint_still_untouched(self, client, org):
        """POST /analyze keeps its single-dataset contract (no regression)."""
        body = {
            "application": org["slug"],
            "dataset": "electricite",
            "analysis": ["summary"],
            "data": _elec_rows(),
        }
        resp = client.post("/api/v1/analyze", json=body, headers=org["headers"])
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["success"] is True
        assert data["dataset"] == "electricite"
        assert "cross_correlations" not in data
