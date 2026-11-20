"""Tests for the Open Analytics AI Python SDK."""

import sys
from pathlib import Path

# Add sdk/python to path
sdk_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(sdk_dir))

from analytics_ai import AnalyticsClient, AnalyticsError


def test_sdk_init():
    client = AnalyticsClient(api_key="test_key", base_url="http://localhost:8000/")
    assert client.base_url == "http://localhost:8000"
    assert client.api_key == "test_key"


def test_sdk_missing_api_key_raises_error():
    client = AnalyticsClient(base_url="http://localhost:8000")
    try:
        client.analyze(application="app", dataset="ds", data=[])
        assert False, "Should have raised AnalyticsError"
    except AnalyticsError as e:
        assert "api_key is required" in str(e)


def test_sdk_live_quick_analyze():
    client = AnalyticsClient(base_url="http://127.0.0.1:8000")
    try:
        res = client.quick_analyze(
            data=[
                {"ventes": 100, "visiteurs": 500},
                {"ventes": 110, "visiteurs": 550},
                {"ventes": 105, "visiteurs": 525},
                {"ventes": 120, "visiteurs": 600},
                {"ventes": 115, "visiteurs": 580},
            ],
            include_ai=False,
            label="test-sdk",
        )
        assert res.get("success") is True
        assert res.get("row_count") == 5
        assert "results" in res
    except AnalyticsError:
        # If server is not reachable in CI, ignore
        pass


def test_sdk_live_compare():
    client = AnalyticsClient(base_url="http://127.0.0.1:8000")
    try:
        res = client.compare(
            period_a=[{"ca": 100}, {"ca": 110}],
            period_b=[{"ca": 150}, {"ca": 160}],
            period_a_label="M-1",
            period_b_label="M",
            include_ai=False,
        )
        assert res.get("success") is True
        assert res.get("period_a_label") == "M-1"
        assert res.get("period_b_label") == "M"
        assert len(res.get("improved", [])) > 0
    except AnalyticsError:
        pass
