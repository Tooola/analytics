"""Tests for period comparator (Feature 3: Comparatif Temporel Automatique)."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.analytics.comparator import PeriodComparator


def test_comparator_identifies_improvements_and_degradations():
    comparator = PeriodComparator()
    data_a = [
        {"ventes": 100, "cout_fcfa": 50, "satisfaction": 80},
        {"ventes": 105, "cout_fcfa": 52, "satisfaction": 82},
        {"ventes": 95, "cout_fcfa": 48, "satisfaction": 78},
    ]
    data_b = [
        {"ventes": 150, "cout_fcfa": 80, "satisfaction": 81},
        {"ventes": 155, "cout_fcfa": 82, "satisfaction": 80},
        {"ventes": 145, "cout_fcfa": 78, "satisfaction": 79},
    ]

    res = comparator.compare(
        period_a_label="Mois M-1",
        period_a_data=data_a,
        period_b_label="Mois M",
        period_b_data=data_b,
    )

    assert res.success is True
    # Ventes progressed -> improved
    improved_metrics = [m.metric for m in res.improved]
    assert "ventes" in improved_metrics

    # Cout_fcfa increased -> degraded (inverted polarity)
    degraded_metrics = [m.metric for m in res.degraded]
    assert "cout_fcfa" in degraded_metrics

    # Satisfaction stayed roughly constant (around 80) -> stable
    stable_metrics = [m.metric for m in res.stable]
    assert "satisfaction" in stable_metrics


def test_comparator_detects_new_anomalies_as_vigilance():
    comparator = PeriodComparator()
    data_a = [
        {"temperature": 22.0}, {"temperature": 22.5}, {"temperature": 23.0},
        {"temperature": 22.1}, {"temperature": 22.8}, {"temperature": 22.3},
        {"temperature": 22.7}, {"temperature": 22.2}, {"temperature": 22.9},
    ]
    # Period B contains extreme spikes
    data_b = [
        {"temperature": 22.0}, {"temperature": 22.5}, {"temperature": 23.0},
        {"temperature": 22.1}, {"temperature": 85.0}, {"temperature": 22.3},
        {"temperature": 22.7}, {"temperature": 92.0}, {"temperature": 22.9},
    ]

    res = comparator.compare(
        period_a_label="S1",
        period_a_data=data_a,
        period_b_label="S2",
        period_b_data=data_b,
    )

    assert len(res.vigilance_points) > 0
    assert any("temperature" in v.metric for v in res.vigilance_points)


def test_zero_correlation_jargon_in_comparator():
    comparator = PeriodComparator()
    data_a = [{"a": 10, "b": 20}, {"a": 12, "b": 24}, {"a": 15, "b": 30}]
    data_b = [{"a": 20, "b": 40}, {"a": 22, "b": 44}, {"a": 25, "b": 50}]

    res = comparator.compare("P1", data_a, "P2", data_b)
    # Ensure no technical correlation jargon
    for group in (res.improved, res.degraded, res.stable):
        for item in group:
            assert "r=" not in item.explanation
            assert "corrélation" not in item.explanation.lower()
    assert "r=" not in res.executive_summary


def test_quick_compare_api_endpoint():
    client = TestClient(app)
    payload = {
        "period_a": {
            "label": "Mois M-1",
            "data": [
                {"ca_eur": 10000, "visiteurs": 500},
                {"ca_eur": 10500, "visiteurs": 520},
                {"ca_eur": 9500, "visiteurs": 480},
            ]
        },
        "period_b": {
            "label": "Mois M",
            "data": [
                {"ca_eur": 14000, "visiteurs": 700},
                {"ca_eur": 14500, "visiteurs": 720},
                {"ca_eur": 13500, "visiteurs": 680},
            ]
        },
        "label": "Comparatif Ventes Mensuelles",
        "include_ai": True,
    }

    response = client.post("/api/v1/analyze/quick/compare", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["period_a_label"] == "Mois M-1"
    assert data["period_b_label"] == "Mois M"
    assert len(data["improved"]) > 0
    assert "executive_summary" in data
    assert data["ai_status"] in ("ok", "error", None)
