"""Segment analysis (``group_by``) — every numeric measure cut by one category.

Every other service only looks at NUMERIC columns: a categorical dimension
(produit, région, canal…) sent by the application was simply ignored. This
service answers the first question a business actually asks — *which segment
carries the number?* — by grouping all numeric measures by ONE categorical
column.

Contract (additive, opt-in through the request's ``group_by``):
- column absent / no usable value → ``segments: []`` + a French ``note``
  (soft-fail: the statistical results stand on their own);
- high cardinality → top ``MAX_SEGMENTS`` by share, with a truncation note;
- ranking metric = first declared numeric column (deterministic);
- each metric carries its own ``share`` (segment sum / total sum over the
  segmented rows, so shares sum to ~1 per metric);
- ``grouped_context_line()`` renders one compact line for the AI prompt —
  build_context() only forwards summary/trend/anomaly, so segments reach the
  provider through the business context instead (engine.py stays untouched).
"""

from __future__ import annotations

from typing import Any

import pandas as pd

# A client_id-like column can hold thousands of values — cap the payload and
# say so (note) rather than stream them all into the response.
MAX_SEGMENTS = 50
# Segments rendered in the AI context line (the response still carries all).
CONTEXT_SEGMENTS = 5


def _empty(group_by: str, note: str) -> dict[str, Any]:
    return {
        "group_by": group_by,
        "ranked_by": None,
        "segment_count": 0,
        "segments": [],
        "note": note,
    }


def build_grouped(
    data: list[dict[str, Any]],
    fields: list[dict[str, Any]],
    group_by: str,
) -> dict[str, Any]:
    """Cut all numeric measures of ``data`` by the ``group_by`` column."""
    group_by = (group_by or "").strip()
    if not group_by:
        return _empty(group_by, "group_by vide")

    df = pd.DataFrame(data)
    if df.empty or group_by not in df.columns:
        return _empty(group_by, f"colonne « {group_by} » absente des données")

    numeric_cols = [
        f["name"]
        for f in fields
        if f.get("technical_type") in ("integer", "float")
        and f["name"] in df.columns
        and f["name"] != group_by  # the dimension is never its own measure
    ]
    if not numeric_cols:
        return _empty(group_by, "aucune colonne numérique à mesurer par segment")

    work = df[df[group_by].notna()].copy()
    if work.empty:
        return _empty(group_by, f"toutes les valeurs de « {group_by} » sont vides")
    work["_segment"] = work[group_by].astype(str)
    for col in numeric_cols:
        work[col] = pd.to_numeric(work[col], errors="coerce")

    # First declared numeric column ranks the segments (deterministic —
    # documented, never guessed from the data).
    ranked_by = numeric_cols[0]
    # Shares are computed over the SEGMENTED rows only, so per metric the
    # shares of the rendered segments sum to ~1.
    totals = {col: float(work[col].sum()) for col in numeric_cols}

    records: list[dict[str, Any]] = []
    for segment, g in work.groupby("_segment", sort=False):
        metrics: dict[str, Any] = {}
        for col in numeric_cols:
            series = g[col].dropna()
            if series.empty:
                continue  # no value for this measure in this segment
            total = totals[col]
            metrics[col] = {
                "count": int(series.count()),
                "mean": round(float(series.mean()), 4),
                "median": round(float(series.median()), 4),
                "min": round(float(series.min()), 4),
                "max": round(float(series.max()), 4),
                "std": round(float(series.std()), 4) if series.count() > 1 else 0.0,
                "sum": round(float(series.sum()), 4),
                "share": round(float(series.sum()) / total, 4) if total else None,
            }
        records.append({
            "segment": str(segment),
            "row_count": int(len(g)),
            "metrics": metrics,
        })

    # Descending by segment total of the ranking metric (share is a constant
    # factor of the same sum — ordering is identical either way).
    def _order(record: dict[str, Any]) -> float:
        metric = record["metrics"].get(ranked_by)
        return -(metric["sum"] if metric else 0.0)

    records.sort(key=_order)

    segment_count = len(records)
    note: str | None = None
    if segment_count > MAX_SEGMENTS:
        records = records[:MAX_SEGMENTS]
        note = (
            f"{MAX_SEGMENTS} premiers segments affichés sur {segment_count} — "
            f"« {group_by} » contient trop de valeurs distinctes "
            f"(classés par somme de « {ranked_by} »)"
        )
    for rank, record in enumerate(records, start=1):
        record["rank"] = rank

    return {
        "group_by": group_by,
        "ranked_by": ranked_by,
        "segment_count": segment_count,
        "segments": records,
        "note": note,
    }


def grouped_context_line(grouped: dict[str, Any] | None) -> str:
    """One compact French line of segment facts, for the AI business context.

    build_context() (engine.py — protected) only forwards summary/trend/
    anomaly, so segments reach the provider as an extra sentence appended to
    the tenant's business context, rebuilt per request.
    """
    if not grouped:
        return ""
    if not grouped.get("segments"):
        note = grouped.get("note")
        return (
            f"Analyse par segment « {grouped.get('group_by')} » — {note}."
            if note
            else ""
        )

    ranked = grouped.get("ranked_by")
    parts: list[str] = []
    for seg in grouped["segments"][:CONTEXT_SEGMENTS]:
        metrics = seg.get("metrics") or {}
        metric = metrics.get(ranked) or next(iter(metrics.values()), None)
        share = metric.get("share") if metric else None
        parts.append(
            f"{seg['segment']} {share * 100:.1f}%"
            if share is not None
            else str(seg["segment"])
        )
    total = grouped.get("segment_count", 0)
    suffix = "…" if total > CONTEXT_SEGMENTS else ""
    line = (
        f"Analyse par segment « {grouped['group_by']} »"
        f"{f' (classé par {ranked})' if ranked else ''} : "
        f"{' · '.join(parts)}{suffix} — {total} segment(s) au total."
    )
    if grouped.get("note"):
        line += f" {grouped['note']}."
    return line
