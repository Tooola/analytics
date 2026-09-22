"""Tests for analytics services: Summary, Trend, Anomaly."""

from __future__ import annotations

import pandas as pd
import pytest
from app.services.analytics.summary import SummaryService
from app.services.analytics.trend import TrendService
from app.services.analytics.anomaly import AnomalyService


class TestSummaryService:
    """Tests for the Summary analytics service."""

    def setup_method(self):
        self.service = SummaryService()

    def test_basic_summary(self):
        df = pd.DataFrame({"revenue": [100, 200, 300, 400, 500]})
        fields = [{"name": "revenue", "technical_type": "float"}]
        result = self.service.run(df, fields)

        assert "summary" in result
        assert len(result["summary"]) == 1
        stats = result["summary"][0]
        assert stats["column"] == "revenue"
        assert stats["count"] == 5
        assert stats["mean"] == 300.0
        assert stats["median"] == 300.0
        assert stats["min"] == 100
        assert stats["max"] == 500

    def test_summary_with_nulls(self):
        df = pd.DataFrame({"value": [10, 20, None, 40, None]})
        fields = [{"name": "value", "technical_type": "float"}]
        result = self.service.run(df, fields)

        assert result["summary"][0]["count"] == 3

    def test_summary_non_numeric_ignored(self):
        df = pd.DataFrame({"name": ["a", "b"], "amount": [10, 20]})
        fields = [
            {"name": "name", "technical_type": "string"},
            {"name": "amount", "technical_type": "float"},
        ]
        result = self.service.run(df, fields)
        columns = [s["column"] for s in result["summary"]]
        assert "name" not in columns
        assert "amount" in columns

    def test_summary_empty_dataframe(self):
        df = pd.DataFrame({"revenue": pd.Series([], dtype=float)})
        fields = [{"name": "revenue", "technical_type": "float"}]
        result = self.service.run(df, fields)
        assert len(result["summary"]) == 0

    def test_summary_multiple_numeric_columns(self):
        df = pd.DataFrame({"revenue": [100, 200], "cost": [50, 80]})
        fields = [
            {"name": "revenue", "technical_type": "float"},
            {"name": "cost", "technical_type": "float"},
        ]
        result = self.service.run(df, fields)
        assert len(result["summary"]) == 2


class TestTrendService:
    """Tests for the Trend analytics service."""

    def setup_method(self):
        self.service = TrendService()

    def test_increasing_trend(self):
        df = pd.DataFrame({
            "date": ["2024-01-01", "2024-02-01", "2024-03-01"],
            "revenue": [100, 150, 200],
        })
        fields = [
            {"name": "date", "technical_type": "date"},
            {"name": "revenue", "technical_type": "float"},
        ]
        result = self.service.run(df, fields)

        assert "trend" in result
        assert len(result["trend"]) == 1
        trend = result["trend"][0]
        assert trend["column"] == "revenue"
        assert trend["direction"] == "up"
        assert trend["change_pct"] > 0

    def test_decreasing_trend(self):
        df = pd.DataFrame({
            "date": ["2024-01-01", "2024-02-01", "2024-03-01"],
            "revenue": [300, 200, 100],
        })
        fields = [
            {"name": "date", "technical_type": "date"},
            {"name": "revenue", "technical_type": "float"},
        ]
        result = self.service.run(df, fields)

        trend = result["trend"][0]
        assert trend["direction"] == "down"
        assert trend["change_pct"] < 0

    def test_stable_trend(self):
        df = pd.DataFrame({
            "date": ["2024-01-01", "2024-02-01", "2024-03-01"],
            "revenue": [100, 101, 100],
        })
        fields = [
            {"name": "date", "technical_type": "date"},
            {"name": "revenue", "technical_type": "float"},
        ]
        result = self.service.run(df, fields)

        trend = result["trend"][0]
        assert trend["direction"] == "stable"

    def test_no_date_field(self):
        df = pd.DataFrame({"revenue": [100, 200, 300]})
        fields = [{"name": "revenue", "technical_type": "float"}]
        result = self.service.run(df, fields)
        assert "trend" in result
        assert len(result["trend"]) == 1

    def test_single_value_no_trend(self):
        df = pd.DataFrame({"revenue": [100]})
        fields = [{"name": "revenue", "technical_type": "float"}]
        result = self.service.run(df, fields)
        assert len(result["trend"]) == 0


class TestAnomalyService:
    """Tests for the Anomaly detection service."""

    def setup_method(self):
        self.service = AnomalyService()

    def test_detects_outliers(self):
        # Use a more extreme outlier to ensure z-score > 3
        normal_values = [10, 12, 11, 13, 10, 12, 11, 10, 12, 11, 500]
        df = pd.DataFrame({"value": normal_values})
        fields = [{"name": "value", "technical_type": "float"}]
        result = self.service.run(df, fields)

        assert "anomaly" in result
        assert len(result["anomaly"]) == 1
        anomalies = result["anomaly"][0]["anomalies"]
        assert len(anomalies) > 0
        assert any(a["value"] == 500 for a in anomalies)

    def test_no_anomalies_in_uniform_data(self):
        df = pd.DataFrame({"value": [10, 10, 10, 10, 10]})
        fields = [{"name": "value", "technical_type": "float"}]
        result = self.service.run(df, fields)
        assert result["anomaly"][0]["count"] == 0

    def test_anomaly_count(self):
        values = list(range(20)) + [1000]
        df = pd.DataFrame({"metric": values})
        fields = [{"name": "metric", "technical_type": "float"}]
        result = self.service.run(df, fields)
        assert result["anomaly"][0]["count"] >= 1

    def test_insufficient_data_no_anomaly(self):
        df = pd.DataFrame({"value": [10, 20]})
        fields = [{"name": "value", "technical_type": "float"}]
        result = self.service.run(df, fields)
        assert len(result["anomaly"]) == 0
