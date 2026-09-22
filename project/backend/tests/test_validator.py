"""Tests for the DataValidator service."""

from __future__ import annotations

import pytest
from app.services.analytics.validator import DataValidator


class TestDataValidator:
    """Tests for data validation against field schemas."""

    def setup_method(self):
        self.validator = DataValidator()

    def test_valid_data_passes(self):
        fields = [
            {"name": "name", "technical_type": "string", "required": True},
            {"name": "amount", "technical_type": "float", "required": True},
        ]
        data = [
            {"name": "Alice", "amount": 100.5},
            {"name": "Bob", "amount": 200.0},
        ]
        result = self.validator.validate(data, fields)
        assert result.valid is True
        assert len(result.errors) == 0

    def test_missing_required_field(self):
        fields = [
            {"name": "name", "technical_type": "string", "required": True},
            {"name": "amount", "technical_type": "float", "required": True},
        ]
        data = [{"name": "Alice"}]
        result = self.validator.validate(data, fields)
        assert result.valid is False
        assert any("amount" in e.field for e in result.errors)

    def test_unknown_column_detected(self):
        fields = [
            {"name": "name", "technical_type": "string", "required": True},
        ]
        data = [{"name": "Alice", "extra_col": 42}]
        result = self.validator.validate(data, fields)
        assert result.valid is False
        assert any("extra_col" in e.field for e in result.errors)

    def test_type_mismatch_integer(self):
        fields = [
            {"name": "count", "technical_type": "integer", "required": True},
        ]
        data = [{"count": "not_a_number"}]
        result = self.validator.validate(data, fields)
        assert result.valid is False
        assert any("count" in e.field for e in result.errors)

    def test_type_mismatch_float(self):
        fields = [
            {"name": "price", "technical_type": "float", "required": True},
        ]
        data = [{"price": "abc"}]
        result = self.validator.validate(data, fields)
        assert result.valid is False

    def test_boolean_validation(self):
        fields = [
            {"name": "active", "technical_type": "boolean", "required": True},
        ]
        assert self.validator.validate([{"active": True}], fields).valid is True
        assert self.validator.validate([{"active": "yes"}], fields).valid is False

    def test_date_validation(self):
        fields = [
            {"name": "created", "technical_type": "date", "required": True},
        ]
        assert self.validator.validate([{"created": "2024-01-15"}], fields).valid is True
        assert self.validator.validate([{"created": "not-a-date"}], fields).valid is False

    def test_empty_data(self):
        fields = [
            {"name": "name", "technical_type": "string", "required": True},
        ]
        result = self.validator.validate([], fields)
        assert result.valid is True
        assert len(result.errors) == 0

    def test_error_cap_at_50(self):
        fields = [
            {"name": f"col_{i}", "technical_type": "integer", "required": True}
            for i in range(100)
        ]
        data = [{f"col_{i}": "bad" for i in range(100)}]
        result = self.validator.validate(data, fields)
        assert len(result.errors) <= 50

    def test_optional_field_not_required(self):
        fields = [
            {"name": "name", "technical_type": "string", "required": True},
            {"name": "nickname", "technical_type": "string", "required": False},
        ]
        data = [{"name": "Alice"}]
        result = self.validator.validate(data, fields)
        assert result.valid is True
