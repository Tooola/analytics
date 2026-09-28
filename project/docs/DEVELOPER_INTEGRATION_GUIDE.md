# Open Analytics AI — Guide d'Explication & d'Intégration Développeur

> **Plateforme réutilisable d'analyses, de détection d'anomalies et d'insights IA pour écosystèmes multi-applications (Farmtinz, CRMtinz, Sharetinz, etc.).**
>
> 🌐 **URL de Production (Railway)** : `https://scintillating-kindness-production-d038.up.railway.app`  
> 💻 **URL Locale (Développement)** : `http://localhost:8000`

---

## 1. 🎯 Vue d'Ensemble & Architecture

Open Analytics AI est un moteur backend centralisé qui reçoit des données brutes en provenance de diverses applications React / Mobile / Python, valide leur conformité par rapport à un schéma enregistré, exécute des calculs statistiques et prédictifs, puis génère des **insights automatiques** ainsi qu'une **interprétation par l'IA**.

```
┌─────────────────────────────────────────────────────────────┐
│  Applications Clientes (Farmtinz, CRMtinz, Sharetinz, etc.) │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP POST /api/v1/analyze
                               │ Header: X-API-Key
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                       FastAPI Backend                       │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 1. Validation de Clé API & Limite de Débit (Middleware) │ │
│ ├─────────────────────────────────────────────────────────┤ │
│ │ 2. Validation du Schéma de Données (DataValidator)      │ │
│ ├─────────────────────────────────────────────────────────┤ │
│ │ 3. Moteur d'Analyse (Summary, Trend, Anomaly)           │ │
│ ├─────────────────────────────────────────────────────────┤ │
│ │ 4. Moteur d'Insights (Règles Métier & Sévérité)          │ │
│ ├─────────────────────────────────────────────────────────┤ │
│ │ 5. Moteur IA Privacy-First (Mock / Gemini / Groq / Ollama)│ │
│ └────────────────────────────┬────────────────────────────┘ │
└──────────────────────────────┼──────────────────────────────┘
                               │ Stockage ORM
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 PostgreSQL / SQLite Database                │
└──────────────────────────────┬──────────────────────────────┘
                               │ Consultation Admin
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             Streamlit Admin Dashboard (Port 8501)           │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. 🛡️ Confidentialité des Données (Privacy-First AI)

Le système garantit que **les données personnelles ou confidentielles brutes ne sont jamais transmises aux modèles de langage (LLM)**.

- Les modules d'analyse calculent des agrégats anonymisés (`AnalyticalContext` : moyennes, pentes de tendance, nombres d'anomalies, types d'insights).
- Seul cet agrégat statistique anonymisé est envoyé au fournisseur IA (`MockAIProvider`, `GeminiProvider`, `GroqProvider` ou `LocalLLMProvider`).

---

## 3. 🌐 Environnements & URLs de Base

L'API est accessible dans deux environnements :

| Environnement | Base URL | Usage |
| :--- | :--- | :--- |
| **Production (Railway)** | `https://scintillating-kindness-production-d038.up.railway.app` | Déploiement en ligne & intégration d'applications distantes |
| **Local (Docker / Uvicorn)** | `http://localhost:8000` | Développement & tests locaux |

> 💡 **Documentation Swagger Interactive (OpenAPI)** :
> - Production : `https://scintillating-kindness-production-d038.up.railway.app/docs`
> - Local : `http://localhost:8000/docs`

---

## 4. 🛠️ Guide d'Intégration Développeur (Pas-à-Pas)

Pour intégrer une nouvelle application (exemple : `Farmtinz`) au moteur d'analyse, suivez ces 3 étapes.

---

### Étape 1 : Enregistrer votre Application (Obtenir une Clé API)

Effectuez une requête `POST /api/v1/applications` pour déclarer votre application. Vous recevrez une clé API unique (`oak_live_...`).

#### Requête :
```bash
curl -X POST "https://scintillating-kindness-production-d038.up.railway.app/api/v1/applications" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Farmtinz",
    "description": "Application de suivi des récoltes et météo agricole"
  }'
```

#### Réponse (`201 Created`) :
```json
{
  "id": "app_9f8d1a2b3c4d",
  "name": "Farmtinz",
  "slug": "farmtinz",
  "status": "active",
  "api_key": "oak_live_a1b2c3d4e5f67890123456789abcdef",
  "created_at": "2026-09-01T18:00:00Z"
}
```

> ⚠️ **IMPORTANT** : Conservez la clé `api_key` en lieu sûr (dans le fichier `.env` de votre serveur backend). Elle ne sera affichée qu'une seule fois.

---

### Étape 2 : Déclarer le Schéma du Jeu de Données (Dataset)

Déclarez la structure des données que votre application va transmettre (nom des colonnes, types techniques, types sémantiques et unités).

Exemple pour le dataset agricole **`farmtinz-harvest`** :

#### Requête :
```bash
curl -X POST "https://scintillating-kindness-production-d038.up.railway.app/api/v1/datasets" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: oak_live_a1b2c3d4e5f67890123456789abcdef" \
  -d '{
    "application_slug": "farmtinz",
    "name": "Farmtinz Harvest",
    "slug": "farmtinz-harvest",
    "description": "Suivi des récoltes, parcelles et météo agricole",
    "fields": [
      {"name": "date", "technical_type": "date", "semantic_type": "date", "required": true},
      {"name": "parcel_id", "technical_type": "string", "semantic_type": "identifier", "required": true},
      {"name": "crop_type", "technical_type": "string", "semantic_type": "category", "required": true},
      {"name": "surface_ha", "technical_type": "float", "semantic_type": "quantity", "unit": "ha", "required": true},
      {"name": "yield_kg", "technical_type": "float", "semantic_type": "quantity", "unit": "kg", "required": true},
      {"name": "temperature_c", "technical_type": "float", "semantic_type": "metric", "unit": "°C", "required": false},
      {"name": "rainfall_mm", "technical_type": "float", "semantic_type": "metric", "unit": "mm", "required": false},
      {"name": "humidity_pct", "technical_type": "integer", "semantic_type": "metric", "unit": "%", "required": false}
    ]
  }'
```

#### Réponse (`201 Created`) :
```json
{
  "id": "ds_7a8b9c0d1e2f",
  "application_id": "app_9f8d1a2b3c4d",
  "name": "Farmtinz Harvest",
  "slug": "farmtinz-harvest",
  "description": "Suivi des récoltes, parcelles et météo agricole",
  "fields": [
    {"id": "fld_1", "name": "date", "technical_type": "date", "semantic_type": "date", "unit": null, "required": true},
    {"id": "fld_2", "name": "parcel_id", "technical_type": "string", "semantic_type": "identifier", "unit": null, "required": true},
    {"id": "fld_3", "name": "crop_type", "technical_type": "string", "semantic_type": "category", "unit": null, "required": true},
    {"id": "fld_4", "name": "surface_ha", "technical_type": "float", "semantic_type": "quantity", "unit": "ha", "required": true},
    {"id": "fld_5", "name": "yield_kg", "technical_type": "float", "semantic_type": "quantity", "unit": "kg", "required": true},
    {"id": "fld_6", "name": "temperature_c", "technical_type": "float", "semantic_type": "metric", "unit": "°C", "required": false},
    {"id": "fld_7", "name": "rainfall_mm", "technical_type": "float", "semantic_type": "metric", "unit": "mm", "required": false},
    {"id": "fld_8", "name": "humidity_pct", "technical_type": "integer", "semantic_type": "metric", "unit": "%", "required": false}
  ],
  "created_at": "2026-09-01T18:05:00Z",
  "updated_at": "2026-09-01T18:05:00Z"
}
```

---

### Étape 3 : Soumettre les Données & Récupérer l'Analyse + Insights

Envoyez les enregistrements bruts au point de terminaison `POST /api/v1/analyze`. Le moteur validera la structure, exécutera les modules statistiques (`summary`, `trend`, `anomaly`) et générera l'interprétation par l'IA si `include_ai: true`.

#### Requête :
```bash
curl -X POST "https://scintillating-kindness-production-d038.up.railway.app/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: oak_live_a1b2c3d4e5f67890123456789abcdef" \
  -d '{
    "application": "farmtinz",
    "dataset": "farmtinz-harvest",
    "analysis": ["summary", "trend", "anomaly"],
    "include_ai": true,
    "data": [
      {"date": "2026-09-01", "parcel_id": "P_01", "crop_type": "Maïs", "surface_ha": 12.5, "yield_kg": 4500, "temperature_c": 24.5, "rainfall_mm": 12.0, "humidity_pct": 65},
      {"date": "2026-09-02", "parcel_id": "P_02", "crop_type": "Blé", "surface_ha": 8.0, "yield_kg": 3200, "temperature_c": 22.0, "rainfall_mm": 5.5, "humidity_pct": 58},
      {"date": "2026-09-03", "parcel_id": "P_03", "crop_type": "Soja", "surface_ha": 15.0, "yield_kg": 5100, "temperature_c": 26.1, "rainfall_mm": 0.0, "humidity_pct": 50},
      {"date": "2026-09-04", "parcel_id": "P_01", "crop_type": "Maïs", "surface_ha": 12.5, "yield_kg": 4650, "temperature_c": 25.0, "rainfall_mm": 25.0, "humidity_pct": 80},
      {"date": "2026-09-05", "parcel_id": "P_04", "crop_type": "Tournesol", "surface_ha": 10.0, "yield_kg": 2800, "temperature_c": 28.4, "rainfall_mm": 0.0, "humidity_pct": 42},
      {"date": "2026-09-06", "parcel_id": "P_02", "crop_type": "Blé", "surface_ha": 8.0, "yield_kg": 3400, "temperature_c": 21.5, "rainfall_mm": 8.0, "humidity_pct": 62},
      {"date": "2026-09-07", "parcel_id": "P_03", "crop_type": "Soja", "surface_ha": 15.0, "yield_kg": 12000, "temperature_c": 27.0, "rainfall_mm": 45.0, "humidity_pct": 88},
      {"date": "2026-09-08", "parcel_id": "P_01", "crop_type": "Maïs", "surface_ha": 12.5, "yield_kg": 4800, "temperature_c": 23.8, "rainfall_mm": 2.0, "humidity_pct": 55}
    ]
  }'
```

#### Réponse de l'API (`200 OK`) :
```json
{
  "id": "run_9a8b7c6d5e4f",
  "application": "farmtinz",
  "dataset": "farmtinz-harvest",
  "status": "completed",
  "row_count": 8,
  "validation": {
    "valid": true,
    "errors": [],
    "row_count": 8
  },
  "results": {
    "summary": [
      {
        "column": "yield_kg",
        "count": 8,
        "mean": 5056.25,
        "median": 4575.0,
        "min": 2800.0,
        "max": 12000.0,
        "std": 2901.87
      },
      {
        "column": "rainfall_mm",
        "count": 8,
        "mean": 12.19,
        "median": 6.75,
        "min": 0.0,
        "max": 45.0,
        "std": 15.34
      }
    ],
    "trend": [
      {
        "column": "yield_kg",
        "direction": "up",
        "change_pct": 6.67,
        "first_value": 4500.0,
        "last_value": 4800.0,
        "periods": 8
      }
    ],
    "anomaly": [
      {
        "column": "yield_kg",
        "method": "zscore",
        "count": 1,
        "anomalies": [
          {
            "row": 6,
            "value": 12000.0,
            "z_score": 2.39,
            "reason": "La valeur 12000.0 kg pour yield_kg est supérieure de 2.39 écarts-types à la moyenne."
          }
        ]
      }
    ]
  },
  "insights": [
    {
      "type": "anomaly",
      "severity": "high",
      "title": "Anomalie détectée sur yield_kg",
      "description": "La parcelle P_03 a enregistré un rendement atypique de 12 000 kg le 2026-09-07."
    },
    {
      "type": "trend",
      "severity": "medium",
      "title": "Tendance à la hausse du rendement",
      "description": "Le rendement yield_kg affiche une progression globale de +6.67% sur les 8 périodes observées."
    }
  ],
  "ai_interpretation": {
    "summary": "L'analyse des 8 relevés de récolte montre une production moyenne de 5 056 kg. Un pic exceptionnel de 12 000 kg sur le Soja (Parcelle P_03) coïncide avec une pluviométrie forte de 45 mm.",
    "recommendations": [
      "Vérifier si la valeur de 12 000 kg sur la parcelle P_03 provient d'une erreur de saisie ou d'un apport d'irrigation exceptionnel.",
      "Consolider les capacités de stockage pour les récoltes de Soja en période de forte pluviométrie."
    ]
  },
  "created_at": "2026-09-24T18:10:00Z"
}
```

---

## 5. 💻 Exemples de Code Client Prêts à l'Emploi

> ⚠️ **IMPORTANT — Principe de Sécurité Fondamental**
>
> La clé d'API (`X-API-Key`) **ne doit JAMAIS être exposée dans le code frontend** (navigateur, React, Next.js public, application mobile).
>
> **Architecture d'Intégration Recommandée :**
> ```
> Application Frontend (React/Mobile)
>              │
>              ▼ Requête interne sans clé API
> Votre Backend Serveur (FastAPI / Node / Django)
>              │
>              ▼ HTTP POST /api/v1/analyze avec X-API-Key
> Open Analytics AI API
> ```

---

### A. Intégration Backend Python / FastAPI (`analytics_service.py`)

Ce service serveur conserve la clé `ANALYTICS_API_KEY` en sécurité et effectue les requêtes vers Open Analytics AI.

```python
# your_backend/services/analytics_service.py
import os
import httpx
from typing import Any

ANALYTICS_API_URL = os.environ.get(
    "ANALYTICS_API_URL", 
    "https://scintillating-kindness-production-d038.up.railway.app"
).rstrip("/")

ANALYTICS_API_KEY = os.environ["ANALYTICS_API_KEY"]  # Clé secrète stockée sur votre serveur

async def analyze_farmtinz_harvest(harvest_records: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Envoie les relevés de récolte à Open Analytics AI et retourne les résultats.
    """
    payload = {
        "application": "farmtinz",
        "dataset": "farmtinz-harvest",
        "analysis": ["summary", "trend", "anomaly"],
        "include_ai": True,
        "data": harvest_records,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{ANALYTICS_API_URL}/api/v1/analyze",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "X-API-Key": ANALYTICS_API_KEY,
            },
        )
        response.raise_for_status()
        return response.json()
```

#### Route Backend exposée à vos clients (React / Mobile) :
```python
# your_backend/api/routes/analytics.py
from fastapi import APIRouter, HTTPException
from your_backend.services.analytics_service import analyze_farmtinz_harvest

router = APIRouter()

@router.post("/api/v1/internal/farmtinz/analyze")
async def run_farmtinz_analysis(records: list[dict]):
    try:
        results = await analyze_farmtinz_harvest(records)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d'analyse : {str(e)}")
```

---

### B. Client Python Synchrone (SDK Léger)

Utile pour les scripts de traitement de données ou les tâches batch :

```python
import os
import requests

class OpenAnalyticsClient:
    def __init__(self, api_url: str | None = None, api_key: str | None = None):
        base = api_url or os.environ.get("ANALYTICS_API_URL", "https://scintillating-kindness-production-d038.up.railway.app")
        self.api_url = base.rstrip("/")
        self.api_key = api_key or os.environ["ANALYTICS_API_KEY"]
        self._headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
        }

    def analyze(self, application: str, dataset: str, data: list[dict], include_ai: bool = True) -> dict:
        url = f"{self.api_url}/api/v1/analyze"
        payload = {
            "application": application,
            "dataset": dataset,
            "analysis": ["summary", "trend", "anomaly"],
            "include_ai": include_ai,
            "data": data,
        }
        resp = requests.post(url, json=payload, headers=self._headers, timeout=30)
        resp.raise_for_status()
        return resp.json()

# Exemple d'utilisation :
if __name__ == "__main__":
    client = OpenAnalyticsClient()
    data = [
        {"date": "2026-09-01", "parcel_id": "P_01", "crop_type": "Maïs", "surface_ha": 12.5, "yield_kg": 4500},
        {"date": "2026-09-02", "parcel_id": "P_02", "crop_type": "Blé", "surface_ha": 8.0, "yield_kg": 3200},
    ]
    report = client.analyze("farmtinz", "farmtinz-harvest", data)
    print("Recommandations IA :", report.get("ai_interpretation", {}).get("recommendations"))
```

---

### C. Intégration Frontend React (`HarvestAnalytics.jsx`)

Le composant React interroge **votre backend intermédiaire**, garantissant la sécurité de la clé API.

```jsx
import React, { useState, useEffect } from 'react';

export function HarvestAnalytics({ harvestData }) {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchAnalysis() {
      try {
        setLoading(true);
        // Appelle VOTRE serveur backend — Aucune clé API exposée dans le navigateur
        const response = await fetch('/api/v1/internal/farmtinz/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(harvestData),
        });

        if (!response.ok) {
          throw new Error(`Erreur HTTP ${response.status}`);
        }

        const data = await response.json();
        setAnalysis(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    if (harvestData && harvestData.length > 0) {
      fetchAnalysis();
    }
  }, [harvestData]);

  if (loading) return <div className="spinner">Analyse des données en cours...</div>;
  if (error) return <div className="alert-error">Impossible de charger l'analyse : {error}</div>;
  if (!analysis) return null;

  return (
    <div className="analytics-card">
      <h2>📊 Tableau de Bord d'Analyse Farmtinz</h2>

      {/* Interprétation & Recommandations IA */}
      {analysis.ai_interpretation && (
        <div className="ai-section">
          <h3>🤖 Synthèse & Recommandations IA</h3>
          <p>{analysis.ai_interpretation.summary}</p>
          <ul>
            {analysis.ai_interpretation.recommendations?.map((rec, idx) => (
              <li key={idx}>{rec}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Alertes d'Insights & Anomalies */}
      {analysis.insights && analysis.insights.length > 0 && (
        <div className="insights-section">
          <h3>⚠️ Insights & Alertes</h3>
          {analysis.insights.map((insight, idx) => (
            <div key={idx} className={`insight-item severity-${insight.severity}`}>
              <strong>{insight.title}</strong> : {insight.description}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

---

## 6. 📋 Types Techniques et Sémantiques Supportés

Lors de la définition de vos jeux de données (`POST /api/v1/datasets`), vous devez spécifier les types pour chaque champ :

### Types Techniques (`technical_type` / `type`) :
- `string` : Texte, identifiants, catégories
- `integer` : Nombres entiers (quantités, compteurs)
- `float` : Nombres décimaux (surfaces, prix, mesures)
- `boolean` : Booleens (`true`/`false`)
- `date` : Dates au format ISO `YYYY-MM-DD` ou `YYYY-MM-DDTHH:MM:SS`

### Types Sémantiques (`semantic_type`) :
- `identifier` : Clé primaire ou référence (ex: `parcel_id`, `lead_id`)
- `date` : Champ temporel pour l'analyse de tendances
- `category` : Variable qualitative pour le regroupement (ex: `crop_type`, `stage`)
- `quantity` : Mesure physique ou comptage (ex: `yield_kg`, `surface_ha`)
- `cost` / `revenue` : Valeurs monétaires (ex: `unit_price`, `total_revenue`)
- `metric` : Indicateur environnemental ou statistique (ex: `temperature_c`, `rainfall_mm`, `humidity_pct`)

---

## 7. 🧪 Tests & Validation de la Plateforme

La suite de tests unitaires et d'intégration garantit la stabilité du moteur :

```bash
# Dans le dossier project/backend :
python -m pytest -v
```

```text
collected 72 items

tests/test_ai_provider.py ......                                         [  8%]
tests/test_analytics.py ..............                                   [ 27%]
tests/test_api.py ....                                                   [ 33%]
tests/test_insights.py ........                                          [ 44%]
tests/test_security.py ..............................                    [ 86%]
tests/test_validator.py ..........                                       [100%]

============================= 72 passed in 5.83s ==============================
```

Tous les **72 tests automatisés** sont au statut `PASSED`.

---

## 8. 🔐 Récapitulatif des Bonnes Pratiques de Sécurité

1. **Jamais de clé API côté frontend** :
   ```env
   ❌ REACT_APP_API_KEY=oak_live_...  (exposé dans le bundle JS)
   ✅ ANALYTICS_API_KEY=oak_live_...  (variable privée du serveur backend)
   ```

2. **Isolation des jeux de données** :
   Chaque application possède sa propre clé d'API. La clé de `Farmtinz` ne peut pas accéder aux datasets de `CRMtinz`.

3. **Confidentialité & RGPD** :
   Aucune donnée personnelle n'est envoyée aux LLMs. Seuls les agrégats statistiques anonymisés alimentent le moteur IA.

4. **Limites de volume** :
   Le moteur accepte jusqu'à **10 000 lignes** de données par appel `/api/v1/analyze`.
