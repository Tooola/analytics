"""Cross-correlation — links BETWEEN datasets aligned on a shared join key.

Feeds the consolidated analysis (POST /analyze/multi): every numeric column
of every dataset is paired with every numeric column of every OTHER dataset,
after aligning rows on the join key (e.g. month). Duplicate keys inside one
dataset are averaged before the alignment so the join never explodes.

Real applications rarely share the exact same grain: one dataset is keyed by
day ("2026-01-15"), another by month ("2026-01"). The key therefore goes
through a granularity rule — ``auto`` (default) normalizes date-parseable
keys to month so both grains meet; ``exact`` keeps raw strings; ``day`` /
``month`` force the normalization. Values that don't parse as dates (regions,
products…) keep raw equality whatever the setting. The alignment actually
reached is returned alongside the links (``cross_correlate_ex``) so callers
can surface "N keys aligned out of M" instead of failing in silence.

Same statistical bar as the intra-dataset CorrelationService: minimum 5
aligned rows, |r| >= 0.4 and p < 0.05.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

MIN_ALIGNED_ROWS = 5
MIN_ABS_R = 0.4
MIN_P_VALUE = 0.05
# Bounds on the O(cols_a * cols_b) pairing so a wide dataset cannot
# turn the consolidated run into thousands of pearson calls.
NUMERIC_COL_CAP = 12
MAX_LINKS = 20
# What the API accepts ("auto" resolves to one of these three).
RESOLVED_GRANULARITIES = ("exact", "day", "month")


def resolve_granularity(
    keys_by_dataset: dict[str, list[str]], requested: str
) -> str:
    """Map a request's ``join_granularity`` to the granularity applied.

    ``auto`` → ``month`` when EVERY key value of EVERY dataset parses as a
    date (day-grain and month-grain then meet on "YYYY-MM"), ``exact``
    otherwise — non-date keys keep raw string equality, i.e. the historical
    behaviour. Explicit ``day`` / ``month`` / ``exact`` are honoured as-is.
    """
    if requested in RESOLVED_GRANULARITIES:
        return requested
    seen = False
    for keys in keys_by_dataset.values():
        if not keys:
            continue
        seen = True
        parsed = pd.to_datetime(
            pd.Series(keys), errors="coerce", format="mixed"
        )
        if parsed.isna().any():
            return "exact"
    return "month" if seen else "exact"


def _normalize_keys(keys: pd.Series, granularity: str) -> pd.Series:
    """``exact`` → raw strings, ``day`` → "YYYY-MM-DD", ``month`` → "YYYY-MM".

    Values that don't parse as a date keep their literal string — they then
    align only when identical on both sides, exactly like ``exact``.
    """
    raw = keys.astype(str)
    if granularity == "exact":
        return raw
    parsed = pd.to_datetime(raw, errors="coerce", format="mixed")
    if granularity == "day":
        norm = parsed.dt.strftime("%Y-%m-%d")
    else:  # month
        norm = parsed.dt.to_period("M").astype(str)
    return norm.where(parsed.notna(), raw)


def _alignment_block(
    keys_by_dataset: dict[str, int],
    aligned_keys: int,
    requested: str,
    granularity: str,
    join_key: str,
) -> dict[str, Any]:
    """Alignment facts + human note for the response and the synthesis."""
    note: str | None = None
    smallest = min(keys_by_dataset.values(), default=0)
    if granularity != "exact":
        label = "mois" if granularity == "month" else "jour"
        note = (
            f"clé normalisée en {label} — {aligned_keys} clé(s) partagée(s) "
            f"entre les jeux"
        )
    elif keys_by_dataset and aligned_keys < smallest:
        note = (
            f"alignement partiel : {aligned_keys} clé(s) partagée(s) sur "
            f"{smallest} — vérifiez que « {join_key} » a le même format et "
            "le même grain dans chaque jeu"
        )
    return {
        "join_key": join_key,
        "requested": requested,
        "granularity": granularity,
        "keys_by_dataset": keys_by_dataset,
        "aligned_keys": aligned_keys,
        "note": note,
    }


def cross_correlate_ex(
    payloads: dict[str, list[dict[str, Any]]],
    fields_by_slug: dict[str, list[dict[str, Any]]],
    join_key: str | None,
    requested: str = "auto",
) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    """Pair numeric columns ACROSS datasets, aligned on ``join_key``.

    Returns ``(links, alignment)``: links sorted by |coefficient| (strongest
    first), capped at ``MAX_LINKS``; ``alignment`` describes the grain
    applied and how many keys actually met (``None`` when no ``join_key`` —
    nothing was attempted, not "no link exists").
    """
    if not join_key:
        return [], None

    # 1. Raw numeric frames per dataset + raw key inventory for detection.
    raw_by_dataset: dict[str, pd.DataFrame] = {}
    keys_by_dataset: dict[str, list[str]] = {}
    for slug, rows in payloads.items():
        df = pd.DataFrame(rows)
        if df.empty or join_key not in df.columns:
            continue
        numeric = [
            f["name"]
            for f in fields_by_slug.get(slug, [])
            if f.get("technical_type") in ("integer", "float")
            and f["name"] in df.columns
        ][:NUMERIC_COL_CAP]
        if not numeric:
            continue
        sub = df[[join_key] + numeric].copy()
        sub[join_key] = sub[join_key].astype(str)
        keys_by_dataset[slug] = sub[join_key].unique().tolist()
        for col in numeric:
            sub[col] = pd.to_numeric(sub[col], errors="coerce")
        raw_by_dataset[slug] = sub

    if len(raw_by_dataset) < 2:
        counts = {slug: len(keys) for slug, keys in keys_by_dataset.items()}
        granularity = resolve_granularity(keys_by_dataset, requested)
        return [], _alignment_block(counts, 0, requested, granularity, join_key)

    # 2. Resolve the grain ONCE, then normalize the key BEFORE averaging
    # duplicates — a day-grain month average is then a true month average.
    granularity = resolve_granularity(keys_by_dataset, requested)
    series_by_dataset: dict[str, pd.DataFrame] = {}
    for slug, sub in raw_by_dataset.items():
        sub[join_key] = _normalize_keys(sub[join_key], granularity)
        # Several rows per period inside one dataset → average them, so the
        # outer join below stays one row per key.
        series_by_dataset[slug] = sub.groupby(join_key, sort=False).mean(
            numeric_only=True
        )

    if len(series_by_dataset) < 2:  # defensive: mirrors the raw count above
        counts = {slug: len(frame) for slug, frame in series_by_dataset.items()}
        return [], _alignment_block(counts, 0, requested, granularity, join_key)

    # 3. Outer-align every dataset on the key; column labels are prefixed
    # with their slug ("ventes.montant") and tracked in col_owner — slugs
    # never contain a dot, so ownership never has to be parsed back out.
    combined: pd.DataFrame | None = None
    col_owner: dict[str, str] = {}
    for slug, sub in series_by_dataset.items():
        renamed = sub.rename(columns=lambda c, s=slug: f"{s}.{c}")
        for col in renamed.columns:
            col_owner[col] = slug
        combined = renamed if combined is None else combined.join(renamed, how="outer")

    if combined is None or combined.empty:
        counts = {slug: len(frame) for slug, frame in series_by_dataset.items()}
        return [], _alignment_block(counts, 0, requested, granularity, join_key)

    # Alignment facts: keys kept per dataset, keys present in >= 2 datasets.
    counts = {slug: len(frame) for slug, frame in series_by_dataset.items()}
    aligned_keys = int((combined.notna().sum(axis=1) >= 2).sum())
    alignment = _alignment_block(counts, aligned_keys, requested, granularity, join_key)

    # 4. Pearson on every cross-dataset column pair.
    cols = list(combined.columns)
    links: list[dict[str, Any]] = []
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            c1, c2 = cols[i], cols[j]
            if col_owner[c1] == col_owner[c2]:
                continue  # intra-dataset links belong to CorrelationService
            pair = combined[[c1, c2]].dropna()
            if len(pair) < MIN_ALIGNED_ROWS:
                continue
            # Constant column → r undefined; skip BEFORE pearsonr warns.
            if pair[c1].nunique() < 2 or pair[c2].nunique() < 2:
                continue
            r, p_val = stats.pearsonr(pair[c1], pair[c2])
            if np.isnan(r) or abs(r) < MIN_ABS_R or p_val >= MIN_P_VALUE:
                continue
            s1 = col_owner[c1]
            s2 = col_owner[c2]
            links.append({
                "dataset1": s1,
                "column1": c1[len(s1) + 1:],
                "dataset2": s2,
                "column2": c2[len(s2) + 1:],
                "coefficient": round(float(r), 4),
                "p_value": round(float(p_val), 4),
                "strength": "strong" if abs(r) >= 0.7 else "moderate",
                "relationship": "positive" if r > 0 else "negative",
            })

    links.sort(key=lambda link: abs(link["coefficient"]), reverse=True)
    return links[:MAX_LINKS], alignment


def cross_correlate(
    payloads: dict[str, list[dict[str, Any]]],
    fields_by_slug: dict[str, list[dict[str, Any]]],
    join_key: str | None,
    requested: str = "auto",
) -> list[dict[str, Any]]:
    """Back-compatible view of ``cross_correlate_ex``: links only."""
    links, _ = cross_correlate_ex(
        payloads, fields_by_slug, join_key, requested=requested
    )
    return links
