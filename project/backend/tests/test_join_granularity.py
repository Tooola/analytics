"""Join granularity — day-grain meets month-grain, alignment never silent.

Feature: cross-dataset links aligned on RAW key strings, so a dataset keyed
by day ("2026-01-15") and one keyed by month ("2026-01") met on ZERO rows and
the response just said ``cross_correlations: []``. The key now goes through a
granularity rule (``join_granularity``: auto/exact/day/month — default auto
keeps raw equality for non-date keys and normalizes date keys to month), and
the alignment actually reached is reported in ``join_alignment`` + carried by
the synthesis.

Additive: new optional request field, new optional response field, existing
month-key behaviour byte-for-byte identical.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.services.analytics import cross_correlation as cc

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


# ─── Unit: granularity resolution & key normalization ───────────────────────


def test_resolve_auto_month_when_all_keys_are_dates():
    keys = {
        "ventes": ["2026-01-05", "2026-01-20", "2026-02-10"],
        "elec": ["2026-01", "2026-02"],
    }
    assert cc.resolve_granularity(keys, "auto") == "month"


def test_resolve_auto_exact_when_any_key_is_not_a_date():
    keys = {"a": ["nord", "sud"], "b": ["nord", "est"]}
    assert cc.resolve_granularity(keys, "auto") == "exact"


def test_resolve_auto_exact_when_keys_mix_dates_and_words():
    keys = {"a": ["2026-01", "inconnu"], "b": ["2026-01"]}
    assert cc.resolve_granularity(keys, "auto") == "exact"


def test_resolve_explicit_values_are_honoured():
    assert cc.resolve_granularity({"a": ["nord"]}, "day") == "day"
    assert cc.resolve_granularity({"a": ["2026-01-05"]}, "exact") == "exact"
    assert cc.resolve_granularity({"a": ["nord"]}, "month") == "month"


def test_normalize_day_keys_merge_to_month():
    import pandas as pd

    keys = pd.Series(["2026-01-05", "2026-01-20", "2026-02-10"])
    out = cc._normalize_keys(keys, "month").tolist()
    assert out == ["2026-01", "2026-01", "2026-02"]


def test_normalize_keeps_unparseable_values_literal():
    import pandas as pd

    keys = pd.Series(["nord", "2026-01-05"])
    out = cc._normalize_keys(keys, "month").tolist()
    assert out[0] == "nord"  # kept as-is: aligns only if identical
    assert out[1] == "2026-01"


def test_normalize_exact_is_plain_string_equality():
    import pandas as pd

    keys = pd.Series(["2026-01-05", "nord"])
    assert cc._normalize_keys(keys, "exact").tolist() == ["2026-01-05", "nord"]


# ─── Fixtures: one day-grain dataset, one month-grain dataset ──────────────

MONTHS = ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06"]
DAYS = ["05", "10", "15", "20", "25"]


def _day_rows():
    """Daily sales — 5 rows per month, perfectly aligned with the months."""
    rows = []
    for i, mois in enumerate(MONTHS):
        value = 1000.0 + 50.0 * i
        for day in DAYS:
            rows.append({"periode": f"{mois}-{day}", "montant": value})
    return rows


def _month_rows():
    """Monthly bills — same underlying progression → r = 1.0 with sales."""
    return [
        {"periode": mois, "montant": 400.0 + 10.0 * i}
        for i, mois in enumerate(MONTHS)
    ]


def _register(client, name):
    resp = client.post("/api/v1/applications", json={"name": name})
    assert resp.status_code == 201, resp.text
    data = resp.json()
    return data["slug"], data["api_key"]


def _create_datasets(client, api_key):
    for name, slug in (("Ventes quotidiennes", "ventes-jour"),
                       ("Factures mensuelles", "factures-mois")):
        resp = client.post(
            "/api/v1/datasets",
            json={
                "name": name,
                "slug": slug,
                "fields": [
                    {"name": "periode", "type": "string", "required": True},
                    {"name": "montant", "type": "float", "required": True},
                ],
            },
            headers={"X-API-Key": api_key},
        )
        assert resp.status_code == 201, resp.text


def _multi_body(slug, **extra):
    body = {
        "application": slug,
        "datasets": ["ventes-jour", "factures-mois"],
        "analysis": ["summary"],
        "join_key": "periode",
        "payloads": {
            "ventes-jour": _day_rows(),
            "factures-mois": _month_rows(),
        },
    }
    body.update(extra)
    return body


# ─── Integration: /analyze/multi ────────────────────────────────────────────


def test_day_and_month_keys_meet_with_auto(client):
    """The core fix: day-grain + month-grain used to align on ZERO rows."""
    slug, key = _register(client, "App Grain Mixte")
    _create_datasets(client, key)
    resp = client.post(
        "/api/v1/analyze/multi",
        json=_multi_body(slug),
        headers={"X-API-Key": key},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()

    # Links found where exact matching found none (r = 1.0 on6 months).
    assert len(data["cross_correlations"]) >= 1
    top = data["cross_correlations"][0]
    assert top["dataset1"] != top["dataset2"]
    assert abs(top["coefficient"] - 1.0) < 1e-6

    alignment = data["join_alignment"]
    assert alignment is not None
    assert alignment["join_key"] == "periode"
    assert alignment["requested"] == "auto"
    assert alignment["granularity"] == "month"
    assert alignment["keys_by_dataset"] == {
        "ventes-jour": 6,  #30 days merged into6 months
        "factures-mois": 6,
    }
    assert alignment["aligned_keys"] == 6
    assert "normalisée en mois" in alignment["note"]

    # The synthesis carries the same facts, and its narrative says so.
    syn = data["synthesis"]
    assert syn["alignment"] == alignment
    assert "Alignement des clés" in syn["summary"]
    assert "Verdict" in syn["summary"]  # narration still closed by the verdict


def test_explicit_exact_keeps_raw_strings_and_reports_the_miss(client):
    """Opt-out works and NEVER fails silently: alignment says why."""
    slug, key = _register(client, "App Grain Exact")
    _create_datasets(client, key)
    resp = client.post(
        "/api/v1/analyze/multi",
        json=_multi_body(slug, join_granularity="exact"),
        headers={"X-API-Key": key},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()

    assert data["cross_correlations"] == []  # what old code always returned
    alignment = data["join_alignment"]
    assert alignment["requested"] == "exact"
    assert alignment["granularity"] == "exact"
    assert alignment["keys_by_dataset"]["ventes-jour"] == 30  # raw day keys
    assert alignment["aligned_keys"] == 0
    assert "alignement partiel" in alignment["note"]
    assert "Alignement des clés" in data["synthesis"]["summary"]


def test_month_grain_default_stays_behaviour_of_yesterday(client):
    """Same-grain datasets: auto resolves to month, keys identical, links kept."""
    slug, key = _register(client, "App Grain Mois")
    _create_datasets(client, key)
    body = _multi_body(slug)
    body["payloads"]["ventes-jour"] = _month_rows()  # both month-grain
    resp = client.post(
        "/api/v1/analyze/multi", json=body, headers={"X-API-Key": key}
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()

    assert len(data["cross_correlations"]) >= 1
    alignment = data["join_alignment"]
    assert alignment["granularity"] == "month"
    assert alignment["aligned_keys"] == 6
    assert alignment["keys_by_dataset"]["ventes-jour"] == 6  # unchanged keys


def test_non_date_keys_keep_exact_equality(client):
    """Categories align raw (auto must NOT treat 'nord' as a date)."""
    slug, key = _register(client, "App Regions")
    for name, slug_ in (("Ventes", "ventes-reg"), ("Coûts", "couts-reg")):
        resp = client.post(
            "/api/v1/datasets",
            json={
                "name": name,
                "slug": slug_,
                "fields": [
                    {"name": "region", "type": "string", "required": True},
                    {"name": "montant", "type": "float", "required": True},
                ],
            },
            headers={"X-API-Key": key},
        )
        assert resp.status_code == 201, resp.text

    regions = ["nord", "sud", "est", "ouest", "centre", "nord-est"]
    resp = client.post(
        "/api/v1/analyze/multi",
        json={
            "application": slug,
            "datasets": ["ventes-reg", "couts-reg"],
            "analysis": ["summary"],
            "join_key": "region",
            "payloads": {
                "ventes-reg": [
                    {"region": r, "montant": 100.0 + 7.0 * i}
                    for i, r in enumerate(regions)
                ],
                "couts-reg": [
                    {"region": r, "montant": 50.0 + 3.0 * i}
                    for i, r in enumerate(regions)
                ],
            },
        },
        headers={"X-API-Key": key},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()

    assert len(data["cross_correlations"]) >= 1  # r =1.0 on6 regions
    alignment = data["join_alignment"]
    assert alignment["granularity"] == "exact"
    assert alignment["aligned_keys"] == 6
    assert alignment["note"] is None  # every key met — nothing to warn about


def test_without_join_key_no_alignment_block(client):
    slug, key = _register(client, "App Sans Clé")
    _create_datasets(client, key)
    body = _multi_body(slug)
    body["join_key"] = None
    resp = client.post(
        "/api/v1/analyze/multi", json=body, headers={"X-API-Key": key}
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["cross_correlations"] == []
    assert data["join_alignment"] is None  # not attempted ≠ "0 aligned"
    assert data["synthesis"]["alignment"] is None


def test_invalid_granularity_value_rejected(client):
    slug, key = _register(client, "App Granularité Faute")
    _create_datasets(client, key)
    resp = client.post(
        "/api/v1/analyze/multi",
        json=_multi_body(slug, join_granularity="week"),
        headers={"X-API-Key": key},
    )
    assert resp.status_code == 422
