# Developer Integration Guide

> **Open Analytics AI** — guide d'intégration sécurisée pour les développeurs.

---

## ⚠️ Principe de sécurité fondamental

**L'API Key doit rester sur votre backend. Jamais dans votre frontend React.**

```
Application React / Mobile
         ↓
Votre Backend (FastAPI / Express / Laravel / etc.)  ← l'API Key est ici
         ↓  HTTPS + X-API-Key
Open Analytics AI API
         ↓
Analytics Engine + AI
         ↓  JSON
Votre Backend
         ↓
React / Frontend
```

**Exemple concret avec Farmtinz :**

```
Farmtinz React (navigateur)
         ↓  (requête interne, sans secret)
Farmtinz Backend Server
         ↓  X-API-Key: anal_xxxx...  (variable d'environnement serveur)
Open Analytics AI API
         ↓
Insights JSON
         ↓
Farmtinz Backend Server
         ↓
Farmtinz React
```

> **Pourquoi ?** Les variables d'environnement d'un bundle React (`REACT_APP_*`, `NEXT_PUBLIC_*`) sont embarquées dans le JavaScript livré au navigateur. N'importe quel utilisateur peut les lire. Une clé secrète ne doit **jamais** être accessible côté navigateur.

---

## Étape 1 — Enregistrer votre application

Enregistrez votre application une seule fois pour obtenir votre clé API.
Cet appel peut être effectué depuis votre terminal ou votre script d'initialisation.

```bash
curl -X POST http://localhost:8000/api/v1/applications \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Farmtinz",
    "description": "Application de gestion agricole"
  }'
```

**Réponse (201 Created) :**

```json
{
  "id": "a1b2c3d4-...",
  "name": "Farmtinz",
  "slug": "farmtinz",
  "status": "active",
  "api_key": "anal_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "created_at": "2026-09-01T10:00:00Z"
}
```

> ⚠️ **La clé `api_key` n'est affichée qu'une seule fois.** Copiez-la immédiatement et stockez-la dans les variables d'environnement de votre **backend** :
>
> ```env
> # Dans le fichier .env de VOTRE backend — jamais commité
> ANALYTICS_API_KEY=anal_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
> ANALYTICS_API_URL=http://analytics-api:8000
> ```

---

## Étape 2 — Déclarer un dataset

Depuis **votre backend**, déclarez la structure des données que vous enverrez :

```bash
curl -X POST http://localhost:8000/api/v1/datasets \
  -H "Content-Type: application/json" \
  -H "X-API-Key: anal_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
  -d '{
    "name": "Récoltes et Ventes",
    "slug": "harvest-sales",
    "description": "Suivi hebdomadaire des récoltes et revenus",
    "fields": [
      {"name": "date",          "type": "date",    "required": true},
      {"name": "culture",       "type": "string",  "required": true},
      {"name": "quantite_kg",   "type": "integer", "required": true,  "unit": "kg"},
      {"name": "prix_unitaire", "type": "float",   "required": true,  "unit": "EUR"},
      {"name": "revenu_total",  "type": "float",   "required": true,  "unit": "EUR"}
    ]
  }'
```

Cet appel est effectué **une seule fois** par dataset (ou lors d'une migration de schéma).

---

## Étape 3 — Envoyer des données et obtenir une analyse

### Architecture correcte

```
React demande une analyse
      ↓
Farmtinz Backend reçoit la requête React
      ↓ (construit le payload + ajoute l'API Key depuis l'environnement)
POST /api/v1/analyze  avec  X-API-Key: anal_xxxx
      ↓
Open Analytics AI répond avec le JSON
      ↓
Farmtinz Backend retourne les résultats à React
```

### Exemple backend Python (FastAPI)

```python
# farmtinz_backend/services/analytics.py
import os
import httpx

ANALYTICS_API_URL = os.environ["ANALYTICS_API_URL"]  # ex: http://analytics-api:8000
ANALYTICS_API_KEY = os.environ["ANALYTICS_API_KEY"]  # clé secrète — jamais dans le frontend

async def run_harvest_analysis(harvest_data: list[dict]) -> dict:
    """Envoie les données de récolte à Open Analytics AI et retourne les insights."""
    payload = {
        "application": "farmtinz",
        "dataset": "harvest-sales",
        "analysis": ["summary", "trend", "anomaly"],
        "include_ai": True,
        "data": harvest_data,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{ANALYTICS_API_URL}/api/v1/analyze",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "X-API-Key": ANALYTICS_API_KEY,  # clé lue depuis l'env serveur
            },
        )
        response.raise_for_status()
        return response.json()
```

```python
# farmtinz_backend/routers/analytics_router.py
from fastapi import APIRouter, Depends
from .services.analytics import run_harvest_analysis

router = APIRouter()

@router.post("/api/analytics/harvest")
async def get_harvest_analytics(data: list[dict]):
    """
    Endpoint appelé par React — sans clé secrète.
    Le backend se charge de l'authentification côté Analytics API.
    """
    results = await run_harvest_analysis(data)
    return results
```

### Exemple backend Node.js (Express)

```javascript
// farmtinz-backend/services/analyticsService.js
const axios = require('axios');

const ANALYTICS_API_URL = process.env.ANALYTICS_API_URL; // variable d'env serveur
const ANALYTICS_API_KEY = process.env.ANALYTICS_API_KEY; // JAMAIS dans le frontend

async function runHarvestAnalysis(harvestData) {
  const response = await axios.post(
    `${ANALYTICS_API_URL}/api/v1/analyze`,
    {
      application: 'farmtinz',
      dataset: 'harvest-sales',
      analysis: ['summary', 'trend', 'anomaly'],
      include_ai: true,
      data: harvestData,
    },
    {
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': ANALYTICS_API_KEY,  // clé serveur uniquement
      },
      timeout: 30000,
    }
  );
  return response.data;
}

module.exports = { runHarvestAnalysis };
```

```javascript
// farmtinz-backend/routes/analytics.js
const express = require('express');
const { runHarvestAnalysis } = require('../services/analyticsService');

const router = express.Router();

// Appelé par React — sans clé secrète
router.post('/harvest-analytics', async (req, res) => {
  try {
    const results = await runHarvestAnalysis(req.body.data);
    res.json(results);
  } catch (err) {
    res.status(500).json({ error: 'Analytics error' });
  }
});

module.exports = router;
```

---

## Étape 4 — Exploiter le résultat dans React

React reçoit le JSON depuis **votre backend** — sans jamais connaître l'API Key :

```jsx
// Farmtinz React — appelle VOTRE backend, pas Analytics API directement
async function fetchHarvestAnalytics(harvestData) {
  const response = await fetch('/api/harvest-analytics', {  // votre backend
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ data: harvestData }),
    // Aucune API Key ici — jamais.
  });
  return response.json();
}

function HarvestDashboard({ harvestData }) {
  const [results, setResults] = useState(null);

  useEffect(() => {
    fetchHarvestAnalytics(harvestData).then(setResults);
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

      <h2>Insights automatiques</h2>
      <InsightCards data={results.insights} />

      {results.ai_interpretation && (
        <div>
          <h2>Interprétation IA</h2>
          <AIInterpretation data={JSON.parse(results.ai_interpretation)} />
        </div>
      )}
    </div>
  );
}
```

---

## Format des données

### Payload d'analyse

| Champ | Type | Description |
|---|---|---|
| `application` | string | Slug de votre application |
| `dataset` | string | Slug du dataset déclaré |
| `analysis` | array | `["summary"]`, `["trend"]`, `["anomaly"]` ou combinaisons |
| `include_ai` | boolean | `true` pour activer l'interprétation IA (optionnel) |
| `data` | array | Lignes de données (max 10 000 lignes par requête) |

### Types de champs supportés

| Type | Format attendu |
|---|---|
| `string` | Texte quelconque |
| `integer` | Nombre entier (`42`) |
| `float` | Nombre décimal (`19.99`) |
| `boolean` | `true` ou `false` |
| `date` | `"YYYY-MM-DD"` |
| `datetime` | `"YYYY-MM-DDTHH:MM:SS"` |

---

## Gestion des autres endpoints

### Récupérer votre profil d'application

```bash
curl http://localhost:8000/api/v1/applications/me \
  -H "X-API-Key: anal_xxxx..."
```

### Lister vos datasets

```bash
curl http://localhost:8000/api/v1/datasets \
  -H "X-API-Key: anal_xxxx..."
```

### Lister vos analyses récentes

```bash
curl http://localhost:8000/api/v1/analysis \
  -H "X-API-Key: anal_xxxx..."
```

### Récupérer le détail d'une analyse

```bash
curl http://localhost:8000/api/v1/analysis/{run_id} \
  -H "X-API-Key: anal_xxxx..."
```

### Lister vos insights

```bash
curl "http://localhost:8000/api/v1/insights?run_id={run_id}" \
  -H "X-API-Key: anal_xxxx..."
```

### Régénérer votre clé API

Si votre clé est compromise, régénérez-la depuis votre backend :

```bash
curl -X POST http://localhost:8000/api/v1/applications/me/regenerate-key \
  -H "X-API-Key: anal_xxxx..."
```

L'ancienne clé est **immédiatement invalide**. Mettez à jour vos variables d'environnement backend.

---

## Security Best Practices

### ❌ Ne faites jamais cela

```javascript
// INTERDIT — expose la clé API dans le navigateur
const API_KEY = process.env.REACT_APP_API_KEY;

fetch('/api/v1/analyze', {
  headers: { 'X-API-Key': API_KEY }  // la clé est visible dans les DevTools
});
```

```env
# INTERDIT dans un fichier frontend .env
REACT_APP_API_KEY=anal_xxxx...
NEXT_PUBLIC_API_KEY=anal_xxxx...
```

### ✅ Faites toujours cela

1. **Stockez la clé côté backend uniquement**
   ```env
   # Dans le .env de votre backend (jamais commité)
   ANALYTICS_API_KEY=anal_xxxx...
   ```

2. **Ne commitez jamais votre `.env`**
   ```gitignore
   # .gitignore
   .env
   .env.local
   *.env
   ```

3. **Utilisez HTTPS en production** pour toutes les communications backend → Analytics API.

4. **Révocation d'urgence** : si une clé est compromise, appelez `/applications/me/regenerate-key` immédiatement depuis votre backend.

5. **N'envoyez que les données nécessaires** : ne transmettez pas toutes vos données client — seulement l'agrégat utile pour l'analyse demandée.

6. **Respectez l'isolation** : chaque application a sa propre clé. La clé de Farmtinz ne peut pas accéder aux données de CRMtinz.

7. **Gérez les erreurs** : vérifiez toujours `results.success` avant d'utiliser les résultats.

8. **Ne loguez pas la clé** : ne laissez jamais la clé apparaître dans vos logs applicatifs.

---

## Dépannage

| Erreur | Cause probable | Solution |
|---|---|---|
| `401 Missing X-API-Key` | Clé absente du header | Vérifiez que votre backend ajoute bien le header `X-API-Key` |
| `401 Invalid or revoked API key` | Clé incorrecte ou révoquée | Vérifiez la valeur de `ANALYTICS_API_KEY` côté backend |
| `403 API key does not match application` | Slug d'application incorrect | Vérifiez que le slug dans le payload correspond à votre application |
| `404 Dataset not found` | Dataset non déclaré ou slug incorrect | Créez le dataset via `POST /api/v1/datasets` |
| `422 Unprocessable Entity` | Payload invalide | Vérifiez les types de champs, les champs requis et la taille des données |

---

## Structure de fichiers clés

- **API Routes** : [`backend/app/api/routes/`](file:///c:/Users/fayom/Downloads/analytics/project/backend/app/api/routes)
- **Moteur Analytique** : [`backend/app/services/analytics/`](file:///c:/Users/fayom/Downloads/analytics/project/backend/app/services/analytics)
- **Fournisseurs IA** : [`backend/app/services/ai/`](file:///c:/Users/fayom/Downloads/analytics/project/backend/app/services/ai)
- **Dashboard Admin** : [`dashboard/app.py`](file:///c:/Users/fayom/Downloads/analytics/project/dashboard/app.py)
