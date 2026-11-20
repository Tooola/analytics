# Open Analytics AI — Python SDK

SDK ultra-léger (0 dépendance externe) pour intégrer le moteur d'analyse décisionnelle et d'explication causale dans vos applications en **1 seule ligne de code**.

## Installation

```bash
pip install open-analytics-ai
```

## Utilisation Rapide (En 1 Ligne)

```python
from analytics_ai import AnalyticsClient

client = AnalyticsClient(base_url="http://localhost:8000")

# 1. Analyse instantanée de données
result = client.quick_analyze(data=[
    {"date": "2026-10-01", "ventes": 150, "visiteurs": 3200, "panier_moyen": 45.2},
    {"date": "2026-10-02", "ventes": 180, "visiteurs": 3500, "panier_moyen": 48.0},
    {"date": "2026-10-03", "ventes": 130, "visiteurs": 2900, "panier_moyen": 44.5},
])

print(result["insights"])
# Moteurs de causalité et explications qualitatives automatiques (sans jargon)
print(result["results"]["causality"])
```

## Comparatif Temporel Automatique (Mois M vs M-1)

Comparez deux périodes temporelles sans jamais devoir fusionner vos fichiers :

```python
comparison = client.compare(
    period_a=[{"ca": 10000, "ventes": 100}, {"ca": 11000, "ventes": 110}],
    period_b=[{"ca": 15000, "ventes": 140}, {"ca": 16000, "ventes": 150}],
    period_a_label="Mois M-1",
    period_b_label="Mois M",
)

# Sort automatiquement les 3 piliers :
print("Ce qui s'est amélioré :", comparison["improved"])
print("Ce qui s'est dégradé :", comparison["degraded"])
print("Points de vigilance :", comparison["vigilance_points"])
```

## Analyse Formelle avec API Key

```python
client = AnalyticsClient(
    api_key="anal_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    base_url="http://localhost:8000"
)

report = client.analyze(
    application="farmtinz",
    dataset="harvest-sales",
    data=[{"date": "2026-10-01", "culture": "Maïs", "quantite_kg": 4500, "prix_unitaire": 0.25, "revenu_total": 1125}]
)
```
