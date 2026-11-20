"""Humanisation des noms techniques de colonnes et alias de lignes.

Transforme les noms bruts (ex: rendement_kg, temperature_c) en libellés
lisibles (ex: Rendement (kg), Température (°C)) pour l'affichage IA et insights.
"""

from __future__ import annotations

# Suffixes d'unités connus → libellé affiché entre parenthèses
_UNIT_SUFFIXES: list[tuple[str, str]] = [
    ("_temperature_c", "Température (°C)"),   # cas complet en priorité
    ("_temp_c",        "Température (°C)"),
    ("_pct",           " (%)"),
    ("_percent",       " (%)"),
    ("_eur",           " (€)"),
    ("_euro",          " (€)"),
    ("_usd",           " ($)"),
    ("_fcfa",          " (FCFA)"),
    ("_xof",           " (XOF)"),
    ("_kg",            " (kg)"),
    ("_mm",            " (mm)"),
    ("_cm",            " (cm)"),
    ("_km",            " (km)"),
    ("_ha",            " (ha)"),
    ("_h",             " (h)"),
    ("_hours",         " (h)"),
    ("_m",             " (m)"),
    ("_c",             " (°C)"),   # doit rester après _temp_c
    ("_k",             " (K)"),
]

# Mots à ne pas capitaliser complètement (articles, prépositions)
_NO_CAPS = {"de", "du", "des", "le", "la", "les", "en", "au", "aux", "par", "et"}


def humanize_column(name: str, unit: str | None = None) -> str:
    """Transforme un nom de colonne technique en libellé lisible.

    Examples
    --------
    >>> humanize_column("rendement_kg")
    'Rendement (kg)'
    >>> humanize_column("taux_chomage_pct")
    'Taux de chômage (%)'
    >>> humanize_column("temperature_c")
    'Température (°C)'
    >>> humanize_column("chiffre_affaires_eur")
    'Chiffre d'affaires (€)'
    >>> humanize_column("revenu", unit="€")
    'Revenu (€)'
    """
    if not name:
        return name or ""

    lower = name.lower()
    detected_unit = ""

    # Cas spéciaux complets (noms entiers connus)
    _FULL_MAP = {
        "temperature_c": "Température (°C)",
        "temp_c": "Température (°C)",
        "rainfall_mm": "Précipitations (mm)",
        "pluviometrie_mm": "Pluviométrie (mm)",
        "taux_chomage_pct": "Taux de chômage (%)",
        "taux_conversion_pct": "Taux de conversion (%)",
        "taux_retour_pct": "Taux de retour (%)",
        "panier_moyen_eur": "Panier moyen (€)",
        "chiffre_affaires_eur": "Chiffre d'affaires (€)",
        "revenu_median_eur": "Revenu médian (€)",
        "revenu_total_eur": "Revenu total (€)",
        "age_median": "Âge médian",
        "surface_ha": "Surface (ha)",
        "yield_kg": "Rendement (kg)",
        "humidity_pct": "Humidité (%)",
        "satisfaction_pct": "Satisfaction (%)",
    }
    if lower in _FULL_MAP:
        return _FULL_MAP[lower]

    # Détection du suffixe d'unité
    label = name
    for suffix, display in _UNIT_SUFFIXES:
        if lower.endswith(suffix):
            # Retirer le suffixe du nom
            base = name[: -len(suffix)]
            if display.startswith(" "):
                # Format "Nom (unité)"
                detected_unit = display
            else:
                # Format remplacement complet (cas temperature)
                return display
            label = base
            break

    # Remplacer underscores par espaces
    words = label.replace("_", " ").split()

    # Capitaliser intelligemment
    result_words = []
    for i, word in enumerate(words):
        if i == 0:
            result_words.append(word.capitalize())
        elif word.lower() in _NO_CAPS:
            result_words.append(word.lower())
        else:
            result_words.append(word.capitalize())

    human = " ".join(result_words)

    # Unité explicite fournie par l'intégrateur (priorité sur détection)
    if unit:
        return f"{human} ({unit})"

    return human + detected_unit


def find_row_identifier(row: dict, idx: int) -> str:
    """Retourne un alias lisible pour une ligne de données.

    Cherche dans la ligne une valeur qui identifie l'entrée (date, nom, région…)
    pour remplacer "ligne #N" dans les textes IA et insights.

    Parameters
    ----------
    row:
        La ligne de données (dict).
    idx:
        Index 0-based de la ligne (utilisé en fallback).

    Returns
    -------
    str
        Ex: "1er juillet 2026", "Région Nord", "2026-07-01", "Observation 7"
    """
    if not row:
        return f"Observation {idx + 1}"

    # Priorité 1 : colonnes temporelles
    _DATE_KEYS = ["date", "datetime", "mois", "month", "semaine", "week",
                  "periode", "period", "annee", "year", "trimestre", "quarter"]
    for key in _DATE_KEYS:
        for col in row:
            if col.lower() == key and row[col] is not None:
                val = str(row[col])
                if len(val) <= 30:
                    return val

    # Priorité 2 : colonnes identifiant textuels
    _ID_KEYS = ["id", "nom", "name", "region", "label", "reference",
                "ref", "code", "categorie", "category", "type", "groupe", "group"]
    for key in _ID_KEYS:
        for col in row:
            if col.lower() == key and row[col] is not None:
                val = str(row[col])
                if 0 < len(val) <= 50:
                    return val

    # Priorité 3 : première colonne texte courte
    for col, val in row.items():
        if isinstance(val, str) and 0 < len(val) <= 40:
            return val

    return f"Observation {idx + 1}"
