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

    def test_unanimous_two_method_confidence_is_full(self):
        """PLAN.md S4: n < 15 → Isolation Forest skipped → a consensus of
        the 2 executed methods must score 1.0, not votes/3 = 0.67."""
        values = [10, 12, 11, 13, 10, 12, 11, 10, 12, 11, 500]
        df = pd.DataFrame({"value": values})
        fields = [{"name": "value", "technical_type": "float"}]
        result = self.service.run(df, fields)

        outlier = next(a for a in result["anomaly"][0]["anomalies"] if a["value"] == 500)
        assert outlier["detected_by"] == ["iqr", "mad"]
        assert outlier["confidence_score"] == 1.0

    def test_confidence_uses_executed_method_count(self):
        """A single-method detection on small n scores 0.5 (1 of 2 executed
        methods), not 0.33 (1 of 3 — a method that never ran)."""
        # 10 detected by IQR only: MAD is disabled (MAD == 0 guard),
        # Isolation Forest skipped (n < 15).
        df = pd.DataFrame({"value": [1, 1, 1, 1, 1, 1, 1, 2, 2, 10]})
        fields = [{"name": "value", "technical_type": "float"}]
        result = self.service.run(df, fields)

        anomalies = result["anomaly"][0]["anomalies"]
        assert len(anomalies) == 1
        assert anomalies[0]["value"] == 10
        assert anomalies[0]["detected_by"] == ["iqr"]
        assert anomalies[0]["confidence_score"] == 0.5


class TestCorrelationService:
    """Tests for the Correlation analytics service."""

    def setup_method(self):
        from app.services.analytics.correlation import CorrelationService
        self.service = CorrelationService()

    def test_strong_positive_correlation(self):
        df = pd.DataFrame({"x": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "y": [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]})
        fields = [{"name": "x", "technical_type": "float"}, {"name": "y", "technical_type": "float"}]
        result = self.service.run(df, fields)
        assert "correlation" in result
        assert len(result["correlation"]) == 1
        corr = result["correlation"][0]
        assert corr["relationship"] == "positive"
        assert corr["coefficient"] > 0.9


class TestDistributionService:
    """Tests for the Distribution analytics service."""

    def setup_method(self):
        from app.services.analytics.distribution import DistributionService
        self.service = DistributionService()

    def test_distribution_metrics(self):
        df = pd.DataFrame({"val": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]})
        fields = [{"name": "val", "technical_type": "float"}]
        result = self.service.run(df, fields)
        assert "distribution" in result
        assert len(result["distribution"]) == 1
        dist = result["distribution"][0]
        assert "percentiles" in dist
        assert dist["percentiles"]["p50"] == 5.5


class TestForecastService:
    """Tests for the Forecast analytics service."""

    def setup_method(self):
        from app.services.analytics.forecast import ForecastService
        self.service = ForecastService()

    def test_forecast_generation(self):
        df = pd.DataFrame({"val": [10, 20, 30, 40, 50]})
        fields = [{"name": "val", "technical_type": "float"}]
        result = self.service.run(df, fields)
        assert "forecast" in result
        assert len(result["forecast"]) == 1
        fore = result["forecast"][0]
        assert len(fore["predictions"]) == 3
        assert fore["trend_direction"] == "up"

    def test_forecast_interval_widens_with_horizon(self):
        """PLAN.md S1: the band must be a real prediction interval that
        strictly grows with the horizon (slope-error bands did not)."""
        # Noisy but trending series → non-zero residual variance.
        df = pd.DataFrame({"val": [10.0, 12.5, 14.1, 17.8, 19.2, 22.6, 24.3, 27.9]})
        fields = [{"name": "val", "technical_type": "float"}]
        result = self.service.run(df, fields)
        preds = result["forecast"][0]["predictions"]

        widths = [p["upper_bound"] - p["lower_bound"] for p in preds]
        assert all(w > 0 for w in widths)
        assert widths[0] < widths[1] < widths[2]

        for p in preds:
            assert p["lower_bound"] <= p["predicted_value"] <= p["upper_bound"]

    def test_forecast_perfect_line_has_zero_width_interval(self):
        """sigma = 0 on a perfect fit → bounds collapse onto the prediction."""
        df = pd.DataFrame({"val": [10, 20, 30, 40, 50]})
        fields = [{"name": "val", "technical_type": "float"}]
        preds = self.service.run(df, fields)["forecast"][0]["predictions"]
        for p in preds:
            assert p["lower_bound"] == p["upper_bound"] == p["predicted_value"]

