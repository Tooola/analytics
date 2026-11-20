"""Automatic analysis selector.

Inspects incoming data characteristics (row count, data types, date columns,
numeric columns) to automatically pick the most relevant analyses for a non-technical
user / executive (e.g., DG), so they do not need to choose technical analysis types.
"""

from __future__ import annotations

from datetime import datetime
import re
from typing import Any

from app.core.logging import get_logger

logger = get_logger(__name__)

DATE_PATTERNS = re.compile(
    r"^(date|time|timestamp|jour|mois|annee|year|month|day|semaine|week|period|created_at|updated_at)$",
    re.IGNORECASE,
)


def _is_date_field(f: dict[str, Any] | Any, sample_values: list[Any]) -> bool:
    """Check if a field represents dates or timestamps."""
    name = f.get("name", "") if isinstance(f, dict) else getattr(f, "name", "")
    tech = f.get("technical_type", "") if isinstance(f, dict) else str(getattr(f, "technical_type", ""))
    sem = f.get("semantic_type", "") if isinstance(f, dict) else str(getattr(f, "semantic_type", "") or "")

    if str(tech).lower() in ("date", "datetime"):
        return True
    if str(sem).lower() == "date":
        return True
    if DATE_PATTERNS.search(name):
        return True

    # Check sample values
    for val in sample_values:
        if val is not None:
            sval = str(val).strip()
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
                try:
                    datetime.strptime(sval, fmt)
                    return True
                except ValueError:
                    pass
            try:
                datetime.fromisoformat(sval)
                return True
            except ValueError:
                pass
    return False


def _is_numeric_field(f: dict[str, Any] | Any, sample_values: list[Any]) -> bool:
    """Check if a field represents numeric values."""
    tech = f.get("technical_type", "") if isinstance(f, dict) else str(getattr(f, "technical_type", ""))
    sem = f.get("semantic_type", "") if isinstance(f, dict) else str(getattr(f, "semantic_type", "") or "")

    if str(tech).lower() in ("integer", "float", "number", "int"):
        return True
    if str(sem).lower() in ("quantity", "metric", "currency", "amount", "rate", "percentage"):
        return True

    # Check sample values
    num_count = sum(1 for v in sample_values if isinstance(v, (int, float)) and not isinstance(v, bool))
    if sample_values and (num_count / len(sample_values)) >= 0.7:
        return True
    return False


def auto_select_analyses(
    data: list[dict[str, Any]],
    fields: list[dict[str, Any]] | list[Any],
) -> list[str]:
    """Select the relevant analysis types based on data structure.

    Rules:
    - 'summary': Always selected (baseline overview)
    - 'trend': Selected if >= 1 date column + >= 1 numeric column + >= 3 rows
    - 'forecast': Selected if >= 1 date column + >= 1 numeric column + >= 5 rows
    - 'anomaly': Selected if >= 1 numeric column + >= 6 rows
    - 'correlation': Selected if >= 2 numeric columns + >= 5 rows
    - 'distribution': Selected if >= 1 numeric column + >= 10 rows

    Returns:
        List of selected analysis type strings.
    """
    row_count = len(data) if data else 0
    if row_count == 0:
        return ["summary"]

    # Sample rows for inspection
    sample_data = data[:20]

    date_cols: list[str] = []
    numeric_cols: list[str] = []

    for f in fields:
        fname = f.get("name", "") if isinstance(f, dict) else getattr(f, "name", "")
        samples = [row.get(fname) for row in sample_data if row.get(fname) is not None]

        if _is_date_field(f, samples):
            date_cols.append(fname)
        if _is_numeric_field(f, samples):
            numeric_cols.append(fname)

    selected: list[str] = ["summary"]

    has_date = len(date_cols) > 0
    has_numeric = len(numeric_cols) > 0

    # Trend: requires time-series capability
    if has_date and has_numeric and row_count >= 3:
        selected.append("trend")

    # Forecast: requires time-series with sufficient points
    if has_date and has_numeric and row_count >= 5:
        selected.append("forecast")

    # Anomaly detection: requires numeric data and enough points
    if has_numeric and row_count >= 6:
        selected.append("anomaly")

    # Correlation: requires at least 2 numeric measures
    if len(numeric_cols) >= 2 and row_count >= 5:
        selected.append("correlation")
        selected.append("causality")

    # Distribution: requires numeric data with enough observations
    if has_numeric and row_count >= 10:
        selected.append("distribution")

    logger.info(
        "Auto-selected analyses for %d rows, %d numeric, %d date: %s",
        row_count,
        len(numeric_cols),
        len(date_cols),
        selected,
    )
    return selected
