"""Data validation service — checks incoming data against a dataset schema."""

from __future__ import annotations

import math
from datetime import datetime
from typing import Any

import pandas as pd

from app.models import DatasetFieldType
from app.schemas.analytics import DataValidationResult, ValidationIssue


class DataValidator:
    """Validates a list of row dicts against a dataset's field definitions."""

    def validate(
        self,
        data: list[dict[str, Any]],
        fields: list[dict[str, Any]],
    ) -> DataValidationResult:
        errors: list[ValidationIssue] = []

        field_map: dict[str, dict[str, Any]] = {f["name"]: f for f in fields}
        required_names = {f["name"] for f in fields if f.get("required", True)}
        known_names = set(field_map.keys())

        for row_idx, row in enumerate(data):
            row_keys = set(row.keys())

            # Missing required columns
            for missing in required_names - row_keys:
                errors.append(ValidationIssue(
                    field=missing,
                    error="Required field is missing",
                    row=row_idx,
                ))

            # Unknown columns
            for unknown in row_keys - known_names:
                errors.append(ValidationIssue(
                    field=unknown,
                    error="Unknown column for this dataset",
                    row=row_idx,
                ))

            # Type checking
            for key, value in row.items():
                if key not in field_map or value is None:
                    continue
                field_def = field_map[key]
                issue = self._check_type(key, value, field_def["technical_type"], row_idx)
                if issue:
                    errors.append(issue)

        return DataValidationResult(
            valid=len(errors) == 0,
            errors=errors[:50],  # cap to keep responses manageable
            row_count=len(data),
        )

    def _check_type(
        self,
        field_name: str,
        value: any,
        expected_type: any,
        row: int,
    ) -> ValidationIssue | None:
        # Convert string to DatasetFieldType enum if needed
        if isinstance(expected_type, str):
            try:
                expected_type = DatasetFieldType(expected_type)
            except ValueError:
                return ValidationIssue(
                    field=field_name,
                    error=f"Unknown field type: {expected_type}",
                    row=row,
                )
        try:
            if expected_type in (DatasetFieldType.integer, DatasetFieldType.float):
                num = float(value)
                if not math.isfinite(num):
                    return ValidationIssue(
                        field=field_name,
                        error="NaN and Infinity values are not allowed",
                        row=row,
                    )
                if expected_type == DatasetFieldType.integer and not num.is_integer():
                    return ValidationIssue(
                        field=field_name, error="Expected integer", row=row,
                    )
            elif expected_type == DatasetFieldType.boolean:
                if not isinstance(value, bool):
                    # Accept 0/1 and "true"/"false" strings
                    if isinstance(value, str):
                        if value.lower() not in ("true", "false"):
                            return ValidationIssue(
                                field=field_name, error="Expected boolean", row=row,
                            )
                    elif isinstance(value, (int, float)):
                        if value not in (0, 1):
                            return ValidationIssue(
                                field=field_name, error="Expected boolean", row=row,
                            )
                    else:
                        return ValidationIssue(
                            field=field_name, error="Expected boolean", row=row,
                        )
            elif expected_type == DatasetFieldType.string:
                if not isinstance(value, str | int | float):
                    return ValidationIssue(
                        field=field_name, error="Expected string", row=row,
                    )
            elif expected_type == DatasetFieldType.date:
                datetime.strptime(str(value), "%Y-%m-%d")
            elif expected_type == DatasetFieldType.datetime:
                datetime.strptime(str(value), "%Y-%m-%dT%H:%M:%S")
        except (ValueError, TypeError):
            return ValidationIssue(
                field=field_name,
                error=f"Expected {expected_type.value}",
                row=row,
            )
        return None
