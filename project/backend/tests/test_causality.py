"""Tests for CausalityService — variance drivers and non-technical explanations."""

from __future__ import annotations

import pandas as pd
from app.services.analytics.causality import CausalityService
from app.schemas.analytics import AnalysisResult


def test_causality_synchronous_variables():
    # ventes and visiteurs move together
    df = pd.DataFrame({
        "ventes_eur": [100, 200, 300, 400, 500, 600],
        "visiteurs": [50, 100, 150, 200, 250, 300],
    })
    service = CausalityService()
    res = service.run(df, [])
    assert "causality" in res
    assert len(res["causality"]) > 0
    driver = res["causality"][0]
    assert driver["relationship_type"] == "synchronous"
    # Must NOT contain raw correlation numbers
    assert "r=" not in driver["explanation"]
    assert "r =" not in driver["explanation"]
    assert "0.9" not in driver["explanation"]
    assert "synchronisée" in driver["explanation"]


def test_causality_opposite_variables():
    # prix increases while volume decreases
    df = pd.DataFrame({
        "prix_eur": [10, 20, 30, 40, 50, 60],
        "volume_unites": [600, 500, 400, 300, 200, 100],
    })
    service = CausalityService()
    res = service.run(df, [])
    assert len(res["causality"]) > 0
    driver = res["causality"][0]
    assert driver["relationship_type"] == "opposite"
    assert "r=" not in driver["explanation"]
    assert "inverse" in driver["explanation"]


def test_causality_segment_contribution():
    # One region dominates 80% of sales
    df = pd.DataFrame({
        "region": ["Nord", "Sud", "Est", "Nord", "Nord"],
        "ventes_eur": [1000, 100, 150, 800, 1200],
    })
    service = CausalityService()
    res = service.run(df, [])
    seg_drivers = [d for d in res["causality"] if d["relationship_type"] == "segment_contribution"]
    assert len(seg_drivers) > 0
    driver = seg_drivers[0]
    assert "Nord" in driver["driver"]
    assert "moteur principal" in driver["explanation"]


def test_analysis_result_schema_with_causality():
    data = {
        "causality": [
            {
                "target": "Ventes (€)",
                "driver": "Visiteurs",
                "relationship_type": "synchronous",
                "explanation": "Les variations de Ventes sont directement synchronisées avec Visiteurs.",
            }
        ]
    }
    result = AnalysisResult(**data)
    assert result.causality is not None
    assert len(result.causality) == 1
    assert result.causality[0].target == "Ventes (€)"
