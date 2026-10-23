"""Business context text — the tenant's own words, fed to the AI.

``AIEngine.build_context`` (``engine.py`` — read-only) assembles the sanitized
AnalyticalContext from statistics alone; the ``business_context`` field of
that context was never populated, so providers fell back to a generic line.
This helper assembles the missing text from data tenants ALREADY provide —
application description, dataset descriptions, column units/semantic types —
so each application gets recommendations in its own vocabulary. Nothing is
required of the caller: empty inputs degrade to today's generic behaviour.

Context is rebuilt per request from THAT tenant's data — there is no global,
fixed context that would leak across applications.
"""

from __future__ import annotations

from typing import Any

MAX_APP_DESCRIPTION = 500
MAX_DATASET_DESCRIPTION = 300
MAX_TOTAL_CHARS = 3000
MAX_COLUMNS_HINTED = 20
MAX_DATASETS_LISTED = 10


def build_business_context(
    app_name: str,
    app_description: str | None,
    datasets: list[dict[str, Any]],
) -> str:
    """Assemble the ``business_context`` string for an AnalyticalContext.

    Each ``datasets`` entry: ``{"name", "slug", "description", "fields":
    [{"name", "unit", "semantic_type", "description"}]}``. Missing pieces are
    skipped — an application that declared nothing gets an empty-ish string
    and the provider's generic fallback still applies.
    """
    parts: list[str] = []

    header = f"Application « {app_name} »"
    desc = (app_description or "").strip()
    if desc:
        header += f" — {desc[:MAX_APP_DESCRIPTION]}"
    parts.append(header + ".")

    for ds in datasets[:MAX_DATASETS_LISTED]:
        name = (ds.get("name") or ds.get("slug") or "").strip()
        slug = (ds.get("slug") or "").strip()
        line = f"« {name} »" if name else ""
        # The AI's merged results are tagged with the SLUG — keep both so the
        # provider can map « Ventes » ↔ "ventes-terrain" in its own output.
        if slug and slug != name:
            line += f" ({slug})" if line else f"({slug})"
        ds_desc = (ds.get("description") or "").strip()
        if ds_desc:
            line += f" — {ds_desc[:MAX_DATASET_DESCRIPTION]}"
        cols = _column_hints(ds.get("fields") or [])
        if cols:
            line += (". " if line else "") + f"Colonnes : {cols}"
        if line:
            parts.append(f"- {line}")

    text = "\n".join(parts)
    if len(text) > MAX_TOTAL_CHARS:
        text = text[: MAX_TOTAL_CHARS - 1] + "…"
    return text


def _column_hints(fields: list[dict[str, Any]]) -> str:
    """`montant (unité : €)` / `date_relevé (date)` — units & semantics only."""
    hints: list[str] = []
    for f in fields[:MAX_COLUMNS_HINTED]:
        name = (f.get("name") or "").strip()
        if not name:
            continue
        details = [
            (f.get("semantic_type") or "").strip(),
            (f"unité : {f['unit'].strip()}" if f.get("unit") else ""),
            (f.get("description") or "").strip(),
        ]
        detail = ", ".join(d for d in details if d)
        hints.append(f"{name} ({detail})" if detail else name)
    return "; ".join(hints)
