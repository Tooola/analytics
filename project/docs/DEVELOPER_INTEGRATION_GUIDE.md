# Open Analytics AI — Guide d'Explication & d'Intégration Développeur

> **Plateforme réutilisable d'analyses, de détection d'anomalies et d'insights IA pour écosystèmes multi-applications (Farmtinz, CRMtinz, Sharetinz, etc.).**

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
│ │ 5. Moteur IA Privacy-First (MockAI / Ollama Local LLM)   │ │
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
- Seul cet agrégat statistique est envoyé au fournisseur IA (`MockAIProvider` ou `LocalLLMProvider`).

---

## 3. 🚀 Guide d'Installation & Démarrage Rapide

### Prérequis
- Python 3.10+
- (Optionnel) Docker & Docker Compose

### Lancement avec Docker (Recommandé)
```bash
docker compose up
```
- **API FastAPI** : `http://localhost:8000`
- **Documentation OpenAPI (Swagger)** : `http://localhost:8000/docs`
- **Dashboard Admin Streamlit** : `http://localhost:8501`

### Lancement Manuel en Local
```bash
# 1. Se placer dans le répertoire backend
cd backend

# 2. Créer et activer l'environnement virtuel
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate # Linux/Mac

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Copier le fichier d'environnement
copy ..\.env.example .env

# 5. Démarrer l'API
uvicorn app.main:app --reload --port 8000

# 6. (Dans un autre terminal) Démarrer le Dashboard Streamlit
cd dashboard
streamlit run app.py
```

---

## 4. 🛠️ Guide d'Intégration Développeur (Pas-à-Pas)

Pour intégrer une nouvelle application (ex: `Farmtinz`) au moteur d'analyse, suivez ces 3 étapes.

---

### Étape 1 : Enregistrer votre Application (Obtenir une Clé API)

Effectuez une requête `POST` pour déclarer l'application. Vous recevrez une clé API unique (ex: `oak_live_...`).

```bash
curl -X POST "http://localhost:8000/api/v1/applications" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Farmtinz",
    "description": "Application de gestion agricole",
    "status": "active"
  }'
```

**Réponse (`201 Created`)** :
```json
{
  "id": "app_9f8d1a2b",
  "name": "Farmtinz",
  "slug": "farmtinz",
  "status": "active",
  "api_key": "oak_live_abc123xyz456...",
  "created_at": "2026-09-01T18:00:00Z"
}
```

> ⚠️ **IMPORTANT** : Conservez la clé `api_key` en lieu sûr (dans votre fichier d'environnement `.env`). Elle ne sera plus réaffichée par l'API.

---

### Étape 2 : Déclarer le Schéma du Jeu de Données (Dataset)

Déclarez la structure des données que vous allez transmettre (nom des colonnes, types techniques et sémantiques).

```bash
curl -X POST "http://localhost:8000/api/v1/datasets" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: oak_live_abc123xyz456..." \
  -d '{
    "application_slug": "farmtinz",
    "name": "Récoltes et Ventes",
    "slug": "harvest-sales",
    "description": "Suivi hebdomadaire des récoltes et revenus",
    "fields": [
      {"name": "date", "type": "date", "semantic_type": "date", "required": true},
      {"name": "culture", "type": "string", "semantic_type": "category", "required": true},
      {"name": "quantite_kg", "type": "integer", "semantic_type": "quantity", "unit": "kg", "required": true},
      {"name": "prix_unitaire", "type": "float", "semantic_type": "cost", "unit": "EUR", "required": true},
      {"name": "revenu_total", "type": "float", "semantic_type": "revenue", "unit": "EUR", "required": true}
    ]
  }'
```

---

### Étape 3 : Soumettre les Données & Récupérer l'Analyse + Insights

Envoyez vos données directement au point de terminaison `/api/v1/analyze`.

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: oak_live_abc123xyz456..." \
  -d '{
    "application_slug": "farmtinz",
    "dataset_slug": "harvest-sales",
    "analysis": ["summary", "trend", "anomaly"],
    "include_ai": true,
    "data": [
      {"date": "2026-08-01", "culture": "Maïs", "quantite_kg": 500, "prix_unitaire": 1.2, "revenu_total": 600.0},
      {"date": "2026-08-08", "culture": "Maïs", "quantite_kg": 550, "prix_unitaire": 1.25, "revenu_total": 687.5},
      {"date": "2026-08-15", "culture": "Maïs", "quantite_kg": 1200, "prix_unitaire": 1.3, "revenu_total": 1560.0}
    ]
  }'
```

**Exemple de Réponse Complète** :
```json
{
  "analysis_id": "run_88f12a",
  "status": "completed",
  "summary": [
    {
      "column": "quantite_kg",
      "count": 3,
      "mean": 750.0,
      "median": 550.0,
      "min": 500,
      "max": 1200,
      "std": 390.5125
    }
  ],
  "trends": [
    {
      "column": "revenu_total",
      "direction": "increasing",
      "slope": 480.0,
      "percentage_change": 160.0
    }
  ],
  "anomalies": [
    {
      "column": "quantite_kg",
      "row_index": 2,
      "value": 1200,
      "reason": "Z-score 2.15 dépasse le seuil"
    }
  ],
  "insights": [
    {
      "type": "opportunity",
      "severity": "HIGH",
      "title": "Forte hausse du revenu_total",
      "description": "Le revenu total présente une tendance à la hausse (+160.0%)."
    }
  ],
  "ai_interpretation": {
    "summary_text": "Les performances de ventes pour Maïs affichent une forte croissance impulsée par la hausse des volumes récoltés.",
    "recommendations": [
      "Augmenter la capacité de stockage pour les récoltes de Maïs.",
      "Surveiller le pic de quantité à 1200 kg pour s'assurer de la stabilité logistique."
    ]
  }
}
```

---

## 5. 💻 Exemples de Code Client

> ⚠️ **IMPORTANT — Principe de sécurité fondamental**
>
> L'API Key doit rester **exclusivement côté backend**. Ne placez jamais une API Key dans :
> - une variable d'environnement React (`REACT_APP_*`)
> - une variable d'environnement Next.js publique (`NEXT_PUBLIC_*`)
> - du code JavaScript livré au navigateur
>
> **Architecture correcte :**
> ```
> React → Votre Backend → Open Analytics AI API
> ```

### Backend Python/FastAPI (`analytics_service.py`)

Cet exemple montre comment votre backend FastAPI appelle Analytics AI avec la clé secrète :

```python
# Votre backend — ex: farmtinz_backend/services/analytics.py
import os
import httpx

ANALYTICS_API_URL = os.environ["ANALYTICS_API_URL"]
ANALYTICS_API_KEY = os.environ["ANALYTICS_API_KEY"]  # variable serveur — jamais dans le frontend

async def run_analysis(app_slug: str, dataset_slug: str, data: list[dict]) -> dict:
    """Appelle Analytics AI depuis le backend — la clé API ne quitte jamais le serveur."""
    payload = {
        "application": app_slug,
        "dataset": dataset_slug,
        "analysis": ["summary", "trend", "anomaly"],
        "include_ai": True,
        "data": data,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{ANALYTICS_API_URL}/api/v1/analyze",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "X-API-Key": ANALYTICS_API_KEY,  # clé serveur uniquement
            },
        )
        response.raise_for_status()
        return response.json()
```

```python
# Votre backend — route exposée à React (sans clé secrète)
from fastapi import APIRouter
router = APIRouter()

@router.post("/api/internal/analytics")
async def get_analytics(data: list[dict]):
    results = await run_analysis("farmtinz", "harvest-sales", data)
    return results  # React reçoit les résultats, jamais la clé
```

### Frontend React (`HarvestDashboard.jsx`)

React appelle **votre backend** — jamais Analytics API directement :

```jsx
// React appelle VOTRE backend — aucune API Key ici
async function fetchAnalytics(harvestData) {
  const response = await fetch('/api/internal/analytics', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(harvestData),
    // Pas de X-API-Key — la clé reste sur votre serveur
  });
  return response.json();
}

function AnalyticsDashboard({ harvestData }) {
  const [results, setResults] = useState(null);

  useEffect(() => {
    fetchAnalytics(harvestData).then(setResults);
  }, [harvestData]);

  if (!results) return <LoadingSpinner />;

  return (
    <div>
      <h2>Résumé statistique</h2>
      <SummaryCards data={results.results?.summary} />

      <h2>Tendances</h2>
      <TrendChart data={results.results?.trend} />

      <h2>Anomalies</h2>
      <AnomalyList data={results.results?.anomaly} />

      <h2>Insights</h2>
      <InsightCards data={results.insights} />
    </div>
  );
}
```

### Client Python direct (backend → Analytics AI)

```python
import requests
import os

class OpenAnalyticsClient:
    def __init__(self):
        self.api_base = os.environ["ANALYTICS_API_URL"].rstrip('/')
        # La clé est lue depuis les variables d'environnement du serveur
        self._headers = {
            "Content-Type": "application/json",
            "X-API-Key": os.environ["ANALYTICS_API_KEY"],
        }

    def analyze(self, app_slug: str, dataset_slug: str, data: list[dict], include_ai: bool = True):
        url = f"{self.api_base}/api/v1/analyze"
        payload = {
            "application": app_slug,
            "dataset": dataset_slug,
            "analysis": ["summary", "trend", "anomaly"],
            "include_ai": include_ai,
            "data": data,
        }
        response = requests.post(url, json=payload, headers=self._headers, timeout=30)
        response.raise_for_status()
        return response.json()
```

---

## 6. 🧪 Exécution des Tests Unitaires

Pour s'assurer du bon fonctionnement de la plateforme :

```bash
cd backend
python -m pytest -v
```

Tous les **41 tests** doivent être au statut `PASSED`.

---

## 7. 📁 Structure des Fichiers Clés

- **API Routes** : [`backend/app/api/routes/`](file:///c:/Users/fayom/Downloads/analytics/project/backend/app/api/routes) (`analytics.py`, `applications.py`, `datasets.py`, `insights.py`)
- **Moteur Analytique** : [`backend/app/services/analytics/`](file:///c:/Users/fayom/Downloads/analytics/project/backend/app/services/analytics) (`summary.py`, `trend.py`, `anomaly.py`, `validator.py`)
- **Moteur d'Insights** : [`backend/app/services/insights/engine.py`](file:///c:/Users/fayom/Downloads/analytics/project/backend/app/services/insights/engine.py)
- **Fournisseurs IA** : [`backend/app/services/ai/`](file:///c:/Users/fayom/Downloads/analytics/project/backend/app/services/ai) (`mock_provider.py`, `local_llm_provider.py`)
- **Script de Démo** : [`backend/scripts/generate_demo_data.py`](file:///c:/Users/fayom/Downloads/analytics/project/backend/scripts/generate_demo_data.py)
- **Dashboard Streamlit** : [`dashboard/app.py`](file:///c:/Users/fayom/Downloads/analytics/project/dashboard/app.py)

---

## 8. 🔐 Security Best Practices

### Ne jamais exposer l'API Key dans le frontend

```
❌ REACT_APP_API_KEY=anal_xxxx    ← visible dans le bundle JS
❌ NEXT_PUBLIC_API_KEY=anal_xxxx  ← visible dans le bundle JS
✅ ANALYTICS_API_KEY=anal_xxxx    ← variable d'env du BACKEND uniquement
```

### Ne jamais committer une API Key

```gitignore
# .gitignore — doit toujours contenir :
.env
.env.local
*.env
```

Utilisez un `.env.example` avec des placeholders uniquement :

```env
ANALYTICS_API_URL=
ANALYTICS_API_KEY=
```

### Utiliser HTTPS en production

Tous les appels backend → Analytics API doivent passer par HTTPS en production.

### Révocation d'urgence

Si une clé est compromise :

```bash
# Depuis votre serveur backend
curl -X POST https://analytics.yourdomain.com/api/v1/applications/me/regenerate-key \
  -H "X-API-Key: anal_old_key..."
```

L'ancienne clé est immédiatement invalide. Mettez à jour vos variables d'environnement.

### Isolation entre applications

Chaque application cliente a sa propre API Key. La clé de Farmtinz ne peut pas accéder aux données de CRMtinz — l'isolation est garantie par le système.

### Limiter les données envoyées

N'envoyez que les données strictement nécessaires à l'analyse demandée. La limite est de **10 000 lignes par requête**.

### Gérer les erreurs proprement

Vérifiez toujours `results.success` avant d'utiliser les données. Ne re-levez pas les erreurs internes brutes vers votre frontend.
