"""Cross-correlation — links BETWEEN datasets aligned on a shared join key.

Feeds the consolidated analysis (POST /analyze/multi): every numeric column
of every dataset is paired with every numeric column of every OTHER dataset,
after aligning rows on the join key (e.g. month). Duplicate keys inside one
dataset are averaged before the alignment so the join never explodes.

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


def cross_correlate(
    payloads: dict[str, list[dict[str, Any]]],
    fields_by_slug: dict[str, list[dict[str, Any]]],
    join_key: str | None,
) -> list[dict[str, Any]]:
    """Pair numeric columns ACROSS datasets, aligned on ``join_key``.

    Returns links sorted by |coefficient| (strongest first), capped at
    ``MAX_LINKS``. Empty list when no ``join_key`` is given or fewer than
    two datasets expose that key — the caller must treat that as "no links
    computed", not "no link exists".
    """
    if not join_key:
        return []

    # 1. One numeric-only frame per dataset, keyed (and averaged) on join_key.
    series_by_dataset: dict[str, pd.DataFrame] = {}
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
        for col in numeric:
            sub[col] = pd.to_numeric(sub[col], errors="coerce")
        # Several rows per period inside one dataset → average them, so the
        # outer join below stays one row per key.
        series_by_dataset[slug] = sub.groupby(join_key, sort=False).mean(numeric_only=True)

    if len(series_by_dataset) < 2:
        return []

    # 2. Outer-align every dataset on the key; column labels are prefixed
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
        return []

    # 3. Pearson on every cross-dataset column pair.
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
    return links[:MAX_LINKS]
