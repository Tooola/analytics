"""Tests for AI providers (Mock and Abstract interface)."""

from __future__ import annotations

import pytest
from app.services.ai.mock_provider import MockAIProvider
from app.schemas.ai import AnalyticalContext


class TestMockAIProvider:
    """Tests for the MockAIProvider."""

    def setup_method(self):
        self.provider = MockAIProvider()

    def test_provider_name(self):
        assert self.provider.name == "mock"

    def test_interpret_returns_structure(self):
        context = AnalyticalContext(
            application="test-app",
            dataset="test-dataset",
            row_count=100,
            summary=[{"column": "revenue", "mean": 500, "count": 100}],
            trends=[{"column": "revenue", "direction": "up", "change_pct": 15.0}],
            anomalies=[{"column": "revenue", "count": 1, "method": "zscore"}],
            insights=[{"type": "trend", "title": "Revenue growing"}],
        )
        result = self.provider.interpret(context)

        assert result.provider == "mock"
        assert result.confidence > 0
        assert result.summary is not None
        assert len(result.key_findings) > 0
        assert len(result.recommendations) > 0

    def test_interpret_with_empty_context(self):
        context = AnalyticalContext(
            application="test-app",
            dataset="test-dataset",
            row_count=0,
            summary=[],
            trends=[],
            anomalies=[],
            insights=[],
        )
        result = self.provider.interpret(context)
        assert result.provider == "mock"
        assert isinstance(result.key_findings, list)
        assert len(result.key_findings) > 0

    def test_interpret_does_not_contain_raw_data(self):
        context = AnalyticalContext(
            application="test-app",
            dataset="test-dataset",
            row_count=50,
            summary=[{"column": "revenue", "mean": 500}],
            trends=[],
            anomalies=[],
            insights=[],
        )
        result = self.provider.interpret(context)
        assert isinstance(result.summary, str)
        assert isinstance(result.key_findings, list)

    def test_interpret_with_trends(self):
        context = AnalyticalContext(
            application="test-app",
            dataset="test-dataset",
            row_count=200,
            summary=[],
            trends=[
                {"column": "revenue", "direction": "up", "change_pct": 25.0},
                {"column": "cost", "direction": "down", "change_pct": -10.0},
            ],
            anomalies=[],
            insights=[],
        )
        result = self.provider.interpret(context)
        assert len(result.key_findings) >= 2

    def test_interpret_with_anomalies(self):
        context = AnalyticalContext(
            application="test-app",
            dataset="test-dataset",
            row_count=100,
            summary=[],
            trends=[],
            anomalies=[{"column": "revenue", "count": 3, "method": "zscore"}],
            insights=[],
        )
        result = self.provider.interpret(context)
        assert any("anomal" in f.lower() for f in result.key_findings)
