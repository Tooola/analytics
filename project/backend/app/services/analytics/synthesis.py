"""Consolidated synthesis — one decision-oriented narrative over N datasets.

Rule-based, deterministic, French business register (same contract as the
insights engine): dominant trend per dataset, divergence between them,
strongest cross-dataset links, risk flags, and a final verdict. This is the
block returned by POST /analyze/multi alongside the raw per-dataset results.
"""

from __future__ import annotations

from typing import Any

_DIR_LABELS = {"up": "hausse", "down": "baisse", "stable": "stable"}

_VERDICT_LABELS = {
    "positif": "dynamique globale positive",
    "equilibre": "équilibre relatif",
    "tension": "tensions entre jeux de données",
    "surveiller": "points à surveiller",
}


def _dominant_direction(trend_entries: list[dict[str, Any]] | None) -> str | None:
    """Direction ("up"/"down"/"stable") of the column with the largest move."""
    best: str | None = None
    best_move = -1.0
    for entry in trend_entries or []:
        direction = entry.get("direction")
        if direction not in _DIR_LABELS:
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
) -> str:
    parts: list[str] = []
    total = sum(row_counts.values())
    aligned = f", alignés sur « {join_key} »" if join_key else ""
    parts.append(
        f"{len(row_counts)} jeu(x) de données analysés en une seule passe "
        f"({total} lignes{aligned})."
    )

    if trends:
        moves = ", ".join(f"{slug} : {_DIR_LABELS[d]}" for slug, d in trends.items())
        parts.append(f"Tendances dominantes — {moves}.")

    if top_links:
        first = top_links[0]
        if first["relationship"] == "positive":
            sens = "évoluent dans le même sens"
        else:
            sens = "évoluent en sens inverse"
        parts.append(
            f"Lien le plus fort : « {first['column1']} » ({first['dataset1']}) et "
            f"« {first['column2']} » ({first['dataset2']}) {sens} "
            f"(r = {first['coefficient']})."
        )
        others = len(top_links) - 1
        if others:
            parts.append(
                f"{others} autre(s) lien(s) significatif(s) entre jeux de données."
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

    if risks:
        parts.append(f"Vigilance — {'; '.join(risks)}.")

    parts.append(f"Verdict : {_VERDICT_LABELS[verdict]}.")
    return " ".join(parts)


def build_synthesis(
    results_by_dataset: dict[str, dict[str, Any]],
    cross_links: list[dict[str, Any]],
    row_counts: dict[str, int],
    join_key: str | None = None,
) -> dict[str, Any]:
    """Build the consolidated decision block from per-dataset results.

    Pure function over data already computed elsewhere — no I/O, fully
    deterministic (the same inputs always produce the same synthesis).
    """
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
            risks.append(f"{slug}: {anomaly_count} anomalie(s) détectée(s)")

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
        "divergent": divergent,
        "top_links": top_links,
        "risks": risks,
        "verdict": verdict,
        "summary": _summary_text(trends, top_links, risks, verdict, join_key, row_counts),
    }
