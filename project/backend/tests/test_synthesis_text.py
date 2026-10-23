"""Consolidated synthesis prose — correct French, honest grain labels.

The summary is what a manager reads first: it must not carry artefacts
like "jeu(x)" / "anomalie(s)", and the grain it announces must match the
join key the caller provided (year keys are never reported as months).
"""

from app.services.analytics.cross_correlation import (
    _alignment_block,
    resolve_granularity,
)
from app.services.analytics.synthesis import build_synthesis

# ─── Year-grain keys resolve to exact, not month ───────────────────────────


def test_resolve_auto_exact_when_all_keys_are_years():
    """"2021"-style keys align by raw equality — the grain is not "month"."""
    keys = {
        "inscriptions": ["2021", "2022", "2023"],
        "concours": ["2021", "2022", "2023"],
    }
    assert resolve_granularity(keys, "auto") == "exact"


def test_year_alignment_note_never_says_month():
    block = _alignment_block(
        {"inscriptions": 5, "concours": 5}, 5, "auto", "exact", "annee"
    )
    assert block["note"] is None  # full exact alignment needs no explanation


def test_month_note_uses_proper_plural():
    block = _alignment_block({"a": 6, "b": 6}, 6, "auto", "month", "mois")
    assert "normalisée en mois" in block["note"]
    assert "6 clés partagées" in block["note"]
    assert "clé(s)" not in block["note"]


def test_partial_note_uses_proper_plural():
    block = _alignment_block({"a": 6, "b": 6}, 1, "auto", "exact", "mois")
    assert "1 clé partagée sur 6" in block["note"]


# ─── Narrative quality ─────────────────────────────────────────────────────

_TWO_DATASETS = {
    "inscriptions-filieres": {
        "trend": [
            {"column": "nb_inscrits", "direction": "stable", "change_pct": 1.0},
        ],
    },
    "concours-acces": {
        "trend": [
            {"column": "nb_admis", "direction": "up", "change_pct": 40.0},
        ],
        "anomaly": [{"column": "nb_admis", "count": 3}],
    },
}

_LINKS = [
    {
        "dataset1": "inscriptions-filieres",
        "column1": "nb_inscrits",
        "dataset2": "concours-acces",
        "column2": "nb_admis",
        "coefficient": 0.9993,
        "p_value": 0.0001,
        "strength": "strong",
        "relationship": "positive",
    },
    {"dataset1": "a", "column1": "x", "dataset2": "b", "column2": "y",
     "coefficient": 0.8, "p_value": 0.01, "strength": "strong",
     "relationship": "positive"},
    {"dataset1": "a", "column1": "p", "dataset2": "b", "column2": "q",
     "coefficient": 0.7, "p_value": 0.02, "strength": "strong",
     "relationship": "positive"},
    {"dataset1": "a", "column1": "m", "dataset2": "b", "column2": "n",
     "coefficient": 0.6, "p_value": 0.03, "strength": "strong",
     "relationship": "positive"},
    {"dataset1": "a", "column1": "k", "dataset2": "b", "column2": "l",
     "coefficient": 0.5, "p_value": 0.04, "strength": "strong",
     "relationship": "positive"},
]

_NAMES = {
    "inscriptions-filieres": "Inscriptions par filière",
    "concours-acces": "Concours d'accès",
}


def _syn(**kwargs):
    return build_synthesis(
        _TWO_DATASETS,
        _LINKS,
        {"inscriptions-filieres": 12, "concours-acces": 13},
        join_key="annee",
        **kwargs,
    )


def test_summary_has_no_placeholder_plurals():
    syn = _syn()
    summary = syn["summary"]
    assert "(s)" not in summary
    assert "(x)" not in summary
    assert "2 jeux de données analysés en une seule passe" in summary
    assert "4 autres liens significatifs" in summary


def test_summary_uses_readable_names_and_prose():
    syn = _syn(dataset_names=_NAMES)
    summary = syn["summary"]
    assert "Tendances dominantes : Inscriptions par filière stable" in summary
    assert "Concours d'accès en hausse" in summary
    # structured fields still keyed by slug
    assert syn["trends"] == {
        "inscriptions-filieres": "stable",
        "concours-acces": "up",
    }
    assert syn["dataset_names"] == _NAMES


def test_risks_use_proper_plural_and_verdict_stays_pinned():
    syn = _syn(dataset_names=_NAMES)
    assert syn["risks"] == ["Concours d'accès : 3 anomalies détectées"]
    assert "Verdict" in syn["summary"]


def test_single_dataset_reads_singular():
    syn = build_synthesis(
        {"boutique": {"trend": [
            {"column": "ca", "direction": "up", "change_pct": 12.0},
        ]}},
        [],
        {"boutique": 48},
    )
    assert "1 jeu de données analysé en une seule passe" in syn["summary"]
