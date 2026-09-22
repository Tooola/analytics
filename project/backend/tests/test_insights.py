"""Tests for the InsightEngine."""

from __future__ import annotations

import pytest
from app.services.insights.engine import InsightEngine


class TestInsightEngine:
    """Tests for insight generation from analysis results."""

    def setup_method(self):
        self.engine = InsightEngine()

    def test_trend_insight_generation(self):
        analysis_results = {
            "trend": [
                {
                    "column": "revenue",
                    "direction": "up",
                    "change_pct": 15.5,
                    "first_value": 1000,
                    "last_value": 1155,
                }
            ]
        }
        insights = self.engine.generate(analysis_results)
        assert len(insights) > 0
        assert any(i["type"] in ("trend", "opportunity") for i in insights)

    def test_anomaly_insight_generation(self):
        analysis_results = {
            "anomaly": [
                {
                    "column": "revenue",
                    "count": 2,
                    "method": "zscore",
                    "anomalies": [
                        {"row": 5, "value": 5000, "z_score": 4.2},
                        {"row": 12, "value": -500, "z_score": -3.5},
                    ],
                }
            ]
        }
        insights = self.engine.generate(analysis_results)
        assert len(insights) > 0
        assert any(i["type"] == "anomaly" for i in insights)

    def test_summary_insight_generation(self):
        analysis_results = {
            "summary": [
                {
                    "column": "revenue",
                    "count": 100,
                    "mean": 500.0,
                    "median": 450.0,
                    "min": 10.0,
                    "max": 2000.0,
                    "std": 300.0,
                }
            ]
        }
        insights = self.engine.generate(analysis_results)
        assert len(insights) > 0
        assert any(i["type"] == "trend" for i in insights)

    def test_empty_results(self):
        insights = self.engine.generate({})
        assert insights == []

    def test_insight_structure(self):
        analysis_results = {
            "trend": [
                {
                    "column": "sales",
                    "direction": "down",
                    "change_pct": -20.0,
                    "first_value": 100,
                    "last_value": 80,
                }
            ]
        }
        insights = self.engine.generate(analysis_results)
        for insight in insights:
            assert "type" in insight
            assert "severity" in insight
            assert "title" in insight
            assert "description" in insight
            assert insight["severity"] in ("low", "medium", "high")

    def test_zero_anomalies_produce_no_insight(self):
        analysis_results = {
            "anomaly": [
                {
                    "column": "revenue",
                    "count": 0,
                    "method": "zscore",
                    "anomalies": [],
                }
            ]
        }
        insights = self.engine.generate(analysis_results)
        assert len(insights) == 0

    def test_high_trend_severity(self):
        analysis_results = {
            "trend": [
                {
                    "column": "revenue",
                    "direction": "down",
                    "change_pct": -30.0,
                    "first_value": 1000,
                    "last_value": 700,
                }
            ]
        }
        insights = self.engine.generate(analysis_results)
        assert insights[0]["severity"] == "high"

    def test_medium_anomaly_severity(self):
        analysis_results = {
            "anomaly": [
                {
                    "column": "revenue",
                    "count": 2,
                    "method": "zscore",
                    "anomalies": [],
                }
            ]
        }
        insights = self.engine.generate(analysis_results)
        assert insights[0]["severity"] == "medium"
