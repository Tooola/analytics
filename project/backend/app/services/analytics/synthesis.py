"""Consolidated synthesis — one decision-oriented narrative over N datasets.

Rule-based, deterministic, French business register (same contract as the
insights engine): dominant trend per dataset, divergence between them,
strongest cross-dataset links, risk flags, and a final verdict. This is the
block returned by POST /analyze/multi alongside the raw per-dataset results.
"""

from __future__ import annotations

from typing import Any

_DIR_LABELS = {
    "fr": {"up": "hausse", "down": "baisse", "stable": "stable"},
    "en": {"up": "increase", "down": "decrease", "stable": "stable"},
}

_DIR_TEXT = {
    "fr": {"up": "en hausse", "down": "en baisse", "stable": "stable"},
    "en": {"up": "increasing", "down": "decreasing", "stable": "stable"},
}

_VERDICT_LABELS = {
    "fr": {
        "positif": "dynamique globale positive",
        "equilibre": "équilibre relatif",
        "tension": "tensions entre jeux de données",
        "surveiller": "points à surveiller",
    },
    "en": {
        "positif": "positive overall dynamic",
        "equilibre": "relative balance",
        "tension": "tensions across datasets",
        "surveiller": "points requiring attention",
    },
}


def _plural(n: int, singular: str, plural: str | None = None, lang: str = "fr") -> str:
    """Pluralisation for the narrative (French & English)."""
    if lang == "en":
        if n == 1:
            return f"1 {singular}"
        return f"{n} {plural or singular + 's'}"
    if n == 1:
        return f"1 {singular}"
    return f"{n} {plural or singular + 's'}"


def _dominant_direction(trend_entries: list[dict[str, Any]] | None) -> str | None:
    """Direction ("up"/"down"/"stable") of the column with the largest move."""
    best: str | None = None
    best_move = -1.0
    for entry in trend_entries or []:
        direction = entry.get("direction")
        if direction not in ("up", "down", "stable"):
            continue
        move = abs(float(entry.get("change_pct") or 0.0))
        if move > best_move:
            best, best_move = direction, move
    return best


def _summary_text(
    trends: dict[str, str],
    top_links: list[dict[str, Any]],
    risks: list[str],
    verdict: str,
    join_key: str | None,
    row_counts: dict[str, int],
    alignment_note: str | None = None,
    dataset_names: dict[str, str] | None = None,
    language: str = "fr",
) -> str:
    """Decision narrative — supports French and English."""
    lang = "en" if language == "en" else "fr"
    names = dataset_names or {}

    def label(slug: str) -> str:
        return names.get(slug) or slug

    parts: list[str] = []
    total = sum(row_counts.values())
    n_ds = len(row_counts)

    if lang == "en":
        aligned = f", aligned on '{join_key}'" if join_key else ""
        parts.append(
            f"{_plural(n_ds, 'dataset', 'datasets', lang='en')} "
            f"analyzed in a single pass ({total} rows{aligned})."
        )

        if trends:
            moves = ", ".join(
                f"{label(slug)} {_DIR_TEXT['en'][d]}" for slug, d in trends.items()
            )
            parts.append(f"Dominant trends: {moves}.")

        if top_links:
            first = top_links[0]
            sens = "move in the same direction" if first["relationship"] == "positive" else "move in opposite directions"
            parts.append(
                f"Strongest link: '{first['column1']}' ({label(first['dataset1'])}) and "
                f"'{first['column2']}' ({label(first['dataset2'])}) {sens}."
            )
            others = len(top_links) - 1
            if others:
                parts.append(
                    f"{others} {'other significant link' if others == 1 else 'other significant links'} "
                    "between datasets."
                )
        elif not join_key:
            parts.append(
                "No cross-dataset link computed: provide join_key (e.g. 'month') "
                "to link datasets together."
            )
        else:
            parts.append(
                "No statistically significant cross-dataset link found over the period."
            )

        if alignment_note:
            parts.append(f"Key alignment — {alignment_note}.")

        if risks:
            parts.append(f"Attention — {'; '.join(risks)}.")

        parts.append(f"Verdict: {_VERDICT_LABELS['en'][verdict]}.")

    else:
        # Default: French
        aligned = f", alignés sur « {join_key} »" if join_key else ""
        parts.append(
            f"{_plural(n_ds, 'jeu', 'jeux', lang='fr')} de données "
            f"{'analysé' if n_ds == 1 else 'analysés'} en une seule passe "
            f"({total} lignes{aligned})."
        )

        if trends:
            moves = ", ".join(
                f"{label(slug)} {_DIR_TEXT['fr'][d]}" for slug, d in trends.items()
            )
            parts.append(f"Tendances dominantes : {moves}.")

        if top_links:
            first = top_links[0]
            sens = "évoluent dans le même sens" if first["relationship"] == "positive" else "évoluent en sens inverse"
            parts.append(
                f"Lien le plus fort : « {first['column1']} » "
                f"({label(first['dataset1'])}) et "
                f"« {first['column2']} » ({label(first['dataset2'])}) {sens}."
            )
            others = len(top_links) - 1
            if others:
                parts.append(
                    f"{others} "
                    f"{'autres liens significatifs' if others > 1 else 'autre lien significatif'} "
                    "entre les jeux de données."
                )
        elif not join_key:
            parts.append(
                "Aucun lien croisé calculé : renseignez join_key (ex. « mois ») "
                "pour relier les jeux entre eux."
            )
        else:
            parts.append(
                "Aucun lien statistiquement significatif entre les jeux de données "
                "sur la période."
            )

        if alignment_note:
            parts.append(f"Alignement des clés — {alignment_note}.")

        if risks:
            parts.append(f"Vigilance — {'; '.join(risks)}.")

        parts.append(f"Verdict : {_VERDICT_LABELS['fr'][verdict]}.")

    return " ".join(parts)


def build_synthesis(
    results_by_dataset: dict[str, dict[str, Any]],
    cross_links: list[dict[str, Any]],
    row_counts: dict[str, int],
    join_key: str | None = None,
    alignment: dict[str, Any] | None = None,
    dataset_names: dict[str, str] | None = None,
    language: str = "fr",
) -> dict[str, Any]:
    """Build the consolidated decision block from per-dataset results.

    Pure function over data already computed elsewhere — no I/O, fully
    deterministic (the same inputs always produce the same synthesis).
    ``alignment`` (optional) reports the grain applied to ``join_key`` and
    how many keys actually met between datasets — surfaced verbatim, and as
    a summary sentence, WITHOUT steering the verdict (verdicts describe the
    data, not the join mechanics). ``dataset_names`` (slug → display name)
    only polishes the prose; structured fields keep the slugs.
    """
    names = dataset_names or {}

    trends: dict[str, str] = {}
    for slug, res in results_by_dataset.items():
        direction = _dominant_direction(res.get("trend"))
        if direction:
            trends[slug] = direction

    directions = set(trends.values())
    divergent = "up" in directions and "down" in directions

    risks: list[str] = []
    for slug, res in results_by_dataset.items():
        anomaly_count = sum(
            int(a.get("count") or 0) for a in (res.get("anomaly") or [])
        )
        if anomaly_count:
            if language == "en":
                det = "detected"
                risks.append(
                    f"{names.get(slug) or slug}: "
                    f"{anomaly_count} anomal{'y' if anomaly_count == 1 else 'ies'} {det}"
                )
            else:
                det = "détectée" if anomaly_count == 1 else "détectées"
                risks.append(
                    f"{names.get(slug) or slug} : "
                    f"{anomaly_count} anomalie"
                    f"{'s' if anomaly_count > 1 else ''} {det}"
                )

    strong = [link for link in cross_links if link.get("strength") == "strong"]
    top_links = strong[:5] or cross_links[:3]

    # Verdict ladder: risk beats divergence beats direction beats neutral.
    if risks:
        verdict = "surveiller"
    elif divergent:
        verdict = "tension"
    elif trends and directions <= {"up", "stable"} and "up" in directions:
        verdict = "positif"
    elif trends and directions <= {"down", "stable"} and "down" in directions:
        verdict = "tension"
    else:
        verdict = "equilibre"

    return {
        "datasets_analyzed": len(results_by_dataset),
        "total_rows": sum(row_counts.values()),
        "join_key": join_key,
        "trends": trends,
        "dataset_names": dict(names),
        "divergent": divergent,
        "top_links": top_links,
        "risks": risks,
        "verdict": verdict,
        "alignment": alignment,
        "summary": _summary_text(
            trends,
            top_links,
            risks,
            verdict,
            join_key,
            row_counts,
            alignment_note=(alignment or {}).get("note"),
            dataset_names=names,
            language=language,
        ),
    }
