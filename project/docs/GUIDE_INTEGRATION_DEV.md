# 🔌 Guide d'intégration développeur — T-ola (Open Analytics AI)

> **Objectif** : appeler **MON API** depuis **votre backend** pour faire analyser vos données
> et récupérer des résultats statistiques, des insights automatiques et une interprétation IA.
>
> ✅ **Toutes les commandes et réponses de ce guide ont été exécutées en live et vérifiées**
> (dernière validation : **15/10/2026**). Vous pouvez tout copier-coller tel quel.
>
> 📖 Référence exhaustive des champs : [`api.md`](api.md) · 🧪 Swagger interactif : `GET /docs`

---

## Sommaire

| # | Section |
|---|---------|
| 0 | [Le parcours en 4 étapes](#0--le-parcours-en-4-étapes) |
| 1 | [Environnements & URLs](#1--environnements--urls) |
| 2 | [Les deux authentifications — à ne pas confondre](#2--les-deux-authentifications--à-ne-pas-confondre) |
| 3 | [Étape 1 — Créer l'application et récupérer la clé](#3--étape-1--créer-lapplication-et-récupérer-la-clé) |
| 4 | [Étape 2 — Déclarer le dataset (le schéma)](#4--étape-2--déclarer-le-dataset--le-schéma-) |
| 5 | [Étape 3 — Analyser un dataset](#5--étape-3--analyser-un-dataset-post-apianalyze) |
| 6 | [Étape 4 — Analyser N datasets en un seul appel](#6--étape-4--analyser-n-datasets-en-un-seul-appel-post-apianalyze-multi) |
| 7 | [Étape 5 — Relire l'historique et les insights](#7--étape-5--relire-lhistorique-et-les-insights) |
| 8 | [Catalogue complet des endpoints](#8--catalogue-complet-des-endpoints) |
| 9 | [Codes d'erreur & gestion côté client](#9--codes-derreur--gestion-côté-client) |
| 10 | [Limites & quotas](#10--limites--quotas) |
| 11 | [Sécurité — les 5 règles](#11--sécurité--les-5-règles) |
| 12 | [Dépannage (FAQ)](#12--dépannage-faq) |
| A | [Annexe — script Python & Node prêts à l'emploi](#a--annexe--scripts-complets) |

---

## 0️⃣ Le parcours en 4 étapes

```
 ÉTAPE 1 (1×)          ÉTAPE 2 (1×/dataset)       ÉTAPE 3 (à chaque usage)
┌────────────────┐     ┌────────────────────┐      ┌─────────────────────────┐
│ POST /         │     │ POST /datasets     │      │ POST /analyze           │
│ applications   │ ──► │ (nom + schéma      │ ──►  │  (1 dataset)            │
│                │     │  des colonnes)     │      │ POST /analyze/multi     │
│ → votre CLÉ    │     └────────────────────┘      │  (N datasets + liens +   │
│   `anal_...`   │                                 │   verdict consolidé)     │
└────────────────┘                                 └───────────┬─────────────┘
                                                               │
                     ÉTAPE 4 (optionnel)                       ▼
              ┌────────────────────────────┐      résultats JSON + insights
              │ GET /analysis  (historique)│      + interprétation IA
              │ GET /insights  (conseils)  │
              └────────────────────────────┘
```

**3 règles absolues :**

1. La clé `X-API-Key` se met dans un **en-tête HTTP** de chaque requête (sauf les 3 endpoints publics — §8).
2. La clé vit **dans les variables d'environnement de votre backend**, jamais dans le navigateur.
3. Les réponses sont du JSON ; les erreurs sont des codes HTTP standards (`401`, `403`, `404`, `422`, `429`).

---

## 1️⃣ Environnements & URLs

| Environnement | Base URL | Usage |
|---|---|---|
| **Local** | `http://localhost:8000` | Développement |
| **Production (Railway)** | `https://scintillating-kindness-production-d038.up.railway.app` | Intégration distante |

Toutes les routes sont préfixées par **`/api/v1`**.

**Documentation auto-générée :**
- Swagger (interactif, on peut tester depuis le navigateur) : `{BASE_URL}/docs`
- Schéma OpenAPI (JSON) : `{BASE_URL}/openapi.json`

**Démarrage local :**

```bash
# Backend (port 8000)
cd project/backend
.venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# Dashboard React (port 5173) — optionnel
cd project/frontend
npm run dev
```

**Vérifier que l'API est vivante** (aucune authentification requise) :

```bash
curl http://localhost:8000/api/v1/health
```

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "ai_provider": "groq",
  "timestamp": "2026-10-15T08:36:39.476735Z"
}
```

> 💡 Si `status` ≠ `healthy` ou que la requête échoue, l'environnement est hors ligne —
> rien à faire côté intégration : le déploiement est à relancer côté infra.

---

## 2️⃣ Les deux authentifications — à ne pas confondre

L'API sert **deux publics différents**, avec deux mécanismes distincts :

| Qui ? | En-tête | Exemple | Pour quels endpoints ? |
|---|---|---|---|
| **Vous — une application tierce** (votre backend) | `X-API-Key` | `X-API-Key: anal_xxx…` | **Tout ce qui concerne vos données** : `/datasets`, `/analyze`, `/analyze/multi`, `/analysis`, `/insights`, `/applications/me` |
| **L'opérateur du dashboard** (interface React) | `Authorization: Bearer <JWT>` | `Authorization: Bearer eyJhbGci…` | Endpoints « opérateur » : `/auth/login`, `/applications/admin/*`, `/datasets/all`, `/datasets/by-app/{slug}` — **pas votre cas d'usage** |
| **Banc d'essai** | aucune | — | `GET /health`, `POST /applications`, `POST /analyze/quick` |

**Votre clé :**
- commence toujours par `anal_` ;
- est propre à **votre application** (isolation totale entre locataires : vos appels ne voient jamais les données d'un autre) ;
- est **hashée en base** : impossible à relire, seule la création et `/me/regenerate-key` la renvoient.

> ⚠️ **`POST /analyze/quick` est public** (pas de clé) : il sert au banc d'essai du dashboard
> (il n'enregistre aucune run). **Ne l'utilisez pas en production** — il n'y a ni isolation ni traçabilité.

---

## 3️⃣ Étape 1 — Créer l'application et récupérer la clé

**Une seule fois**, depuis votre terminal ou votre script d'installation :

```bash
curl -X POST http://localhost:8000/api/v1/applications \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ma Structure",
    "description": "Analyse financière multi-départements"
  }'
```

**Réponse `201 Created`** (vraie sortie) :

```json
{
  "id": "ffff7a62-42e4-42c8-ac98-1a9429098b2c",
  "name": "Ma Structure",
  "slug": "ma-structure",
  "description": "Analyse financière multi-departements",
  "status": "active",
  "api_key": "anal_LloHq…",
  "created_at": "2026-10-15T08:36:39.476735Z",
  "updated_at": "2026-10-15T08:36:39.476735Z"
}
```

> ⚠️ **`api_key` n'est affichée QU'UNE FOIS.** Copiez-la immédiatement dans vos variables
> d'environnement backend — elle n'apparaîtra plus jamais :
>
> ```env
> # .env de VOTRE backend — jamais commité, jamais côté navigateur
> ANALYTICS_API_KEY=anal_LloHq…
> ANALYTICS_API_URL=http://localhost:8000
> ```
>
> **PowerShell** : les guillemets du JSON inline sont mangés par PowerShell → écrivez le corps
> dans un fichier (`payload.json`) et utilisez `-d "@payload.json"`. (Voir §12.)

> 💡 **Décrivez votre application (`description`).** Ce texte devient le *contexte métier*
> transmis à l'IA à chaque analyse : elle oriente alors constats et recommandations vers
> VOTRE domaine (agricole, financier, logistique…) au lieu d'un vocabulaire générique.
> Modifiable à tout moment via `PUT /api/v1/applications/me`. Texte libre, facultatif —
> mais c'est **le levier n°1** pour des recommandations vraiment contextualisées.

**Gestion de la clé ensuite :**

| Action | Endpoint | Retour |
|---|---|---|
| Profil de mon app | `GET /api/v1/applications/me` | `200` profil |
| Renouveler la clé (l'ancienne est **invalidée**) | `POST /api/v1/applications/me/regenerate-key` | `200` `{"api_key": "anal_…"}` — **affichée une fois** |
| Révoquer la clé (app non analysable) | `POST /api/v1/applications/me/revoke-key` | `204` |

---

## 4️⃣ Étape 2 — Déclarer le dataset (le schéma)

Le **dataset** = le modèle de vos colonnes. L'API s'en sert pour **valider chaque ligne** que
vous envoyez ensuite (type, champ requis…). Un dataset est propre à votre application ;
son `slug` doit être unique **au sein de votre app**.

```bash
curl -X POST http://localhost:8000/api/v1/datasets \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $ANALYTICS_API_KEY" \
  -d '{
    "name": "Ventes terrain",
    "slug": "ventes-terrain",
    "fields": [
      {"name": "mois",     "type": "string", "required": true},
      {"name": "montant",  "type": "float",  "required": true}
    ]
  }'
```

**Réponse `201 Created`** (vraie sortie, extraits) :

```json
{
  "id": "90d3c38e-…",
  "application_id": "ffff7a62-…",
  "name": "Ventes terrain",
  "slug": "ventes-terrain",
  "fields": [
    {"id": "…", "name": "mois",    "technical_type": "string", "semantic_type": null, "unit": null, "required": true, "description": null},
    {"id": "…", "name": "montant", "technical_type": "float",  "semantic_type": null, "unit": null, "required": true, "description": null}
  ]
}
```

**Types de champs acceptés** (champ `type`, alias de `technical_type`) :

| Type | Attendu dans vos lignes | Exemple |
|---|---|---|
| `string` | texte | `"2026-01"` |
| `number`/`integer` | entier | `42` |
| `float` | décimal | `15983.33` |
| `boolean` | booléen | `true` |
| `date` | date ISO | `"2026-01-15"` |
| `datetime` | date-heure ISO | `"2026-01-15T10:30:00Z"` |

**Champs optionnels d'une colonne :** `description`, `unit` (`"€"`, `"kg"`), `semantic_type`
(`"date"`, `"quantity"`, `"category"`).

> 💡 **Renseignez-les.** `unit` / `semantic_type` / `description` sont injectés dans le
> *contexte métier* de l'IA : elle peut alors écrire « en euros », « par kilogramme » ou
> reconnaître une date de pertinence — et pas rester générique. Le `slug` du dataset est
> transmis tel quel : l'IA relie ainsi ses résultats (tagués par slug) à vos intitulés.

**Autres endpoints dataset :**

| Action | Endpoint |
|---|---|
| Lister **mes** datasets (paginé : `?skip=0&limit=100`, max 500) | `GET /api/v1/datasets` |
| Détail | `GET /api/v1/datasets/{dataset_id}` |
| Modifier | `PUT /api/v1/datasets/{dataset_id}` |
| Supprimer | `DELETE /api/v1/datasets/{dataset_id}` → `204` |

---

## 5️⃣ Étape 3 — Analyser un dataset (`POST /api/v1/analyze`)

Vous envoyez vos **lignes brutes** + le slug du dataset. L'API valide, analyse, trace la run
et (optionnellement) fait rédiger une interprétation IA.

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $ANALYTICS_API_KEY" \
  -d '{
    "application": "ma-structure",
    "dataset": "ventes-terrain",
    "analysis": ["summary", "trend", "anomaly"],
    "include_ai": true,
    "data": [
      {"mois": "2026-01", "montant": 12000},
      {"mois": "2026-02", "montant": 15500},
      {"mois": "2026-03", "montant": 14800},
      {"mois": "2026-04", "montant": 17200},
      {"mois": "2026-05", "montant": 16900},
      {"mois": "2026-06", "montant": 19500}
    ]
  }'
```

> 💡 Les alias `application_slug` / `dataset_slug` sont acceptés à la place de `application` / `dataset`.

**Réponse `200`** (vraie sortie, `include_ai: false`) :

```json
{
  "success": true,
  "analysis_id": "58d678f5-74b4-4237-a4e5-f2b2555471d2",
  "application": "guide-test-dev",
  "dataset": "ventes-terrain",
  "validation": {"valid": true, "errors": [], "row_count": 6},
  "results": {
    "summary": [
      {"count": 6, "mean": 15983.3333, "median": 16200.0, "min": 12000.0,
       "max": 19500.0, "std": 2537.2557, "column": "montant"}
    ],
    "trend": [
      {"column": "montant", "change_pct": 62.5, "direction": "up",
       "first_value": 12000.0, "last_value": 19500.0, "periods": 6}
    ],
    "anomaly": [
      {"column": "montant", "anomalies": [], "count": 0,
       "method": "ensemble (iqr + mad + isolation_forest)"}
    ],
    "correlation": null,
    "distribution": null,
    "forecast": null
  },
  "insights": [
    {"id": "210e6003-…", "type": "trend", "severity": "low",
     "title": "Vue d'ensemble — montant",
     "description": "Sur 6 enregistrements analysés, la valeur moyenne de **montant** est de **15,983.33** (médiane : 16,200.00, min : 12000.0, max : 19500.0).",
     "metric": "montant", "value": null, "unit": null, "confidence": 1.0},
    {"id": "03d6642d-…", "type": "opportunity", "severity": "high",
     "title": "Progression de +62.5% sur montant",
     "description": "L'indicateur montant progresse de +62.5% sur 6 périodes. Trajectoire positive confirmée sur la période.",
     "metric": "montant", "value": 62.5, "unit": "%", "confidence": 0.95}
  ],
  "ai_interpretation": null
}
```

**Lire la réponse :**

| Bloc | Contenu |
|---|---|
| `validation` | Contrôle du schéma. `errors[]` = `{field, error, row}` ligne par ligne fautive |
| `results` | Résultats **par type d'analyse demandé** (les non demandés = `null`) |
| `insights` | Conseils générés par règles : `type` (`trend`, `anomaly`, `risk`, `forecast`, `opportunity`, `recommendation`), `severity` (`low`/`medium`/`high`), `confidence` |
| `ai_interpretation` | `null` ici (include_ai false). Avec `include_ai: true` → **une chaîne JSON** à parser (voir ci-dessous) |
| `ai_status` | Statut honnête de l'IA : `null` = non demandée, `"ok"` = interprétation livrée, `"error"` = demandée mais fournisseur en panne (**vos résultats statistiques sont quand même là** — plus de `null` silencieux). Idem sur `/analyze/multi` et `/analyze/quick` |
| `analysis_id` | UUID de la run — réutilisable avec `GET /analysis/{id}` |

**Types d'analyse disponibles** (dans `analysis[]`) :

| Type | Calcule |
|---|---|
| `summary` | count / mean / median / min / max / std par colonne numérique |
| `trend` | direction (up/down/stable), % d'évolution, périodes |
| `anomaly` | valeurs aberrantes (IQR + MAD + isolation forest) |
| `correlation` | paires de colonnes corrélées (Pearson, \|r\| ≥ 0.4, p < 0.05) |
| `distribution` | histogrammes / répartition |
| `forecast` | prévision sur les périodes suivantes |

**Avec l'IA activée** (`include_ai: true`), `ai_interpretation` est une **chaîne** contenant :

```jsonc
{
  "provider": "groq",                  // ou "mock", "gemini", "ollama"
  "summary": "Les ventes de terrain affichent une moyenne de 15 983…",
  "key_findings": ["Le montant moyen … +62,5 % sur six périodes", "…"],
  "recommendations": ["Exploiter la forte hausse …", "…"],
  "action_plan": ["…"],
  "risk_assessment": "…",              // ou null
  "confidence": 0.96
}
```

> 🔒 **Privacy-first** : l'IA ne reçoit **jamais vos lignes brutes**, uniquement des agrégats
> anonymisés (moyennes, pentes, nombres d'anomalies, insights).

### ⚠️ Le cas « échec de validation » : `200` + `success: false`

Si vos données **ne respectent pas le schéma** déclaré, l'HTTP reste `200` mais :

```json
{
  "success": false,
  "analysis_id": "7dbe3519-1b71-40e5-8b18-2cb50250f919",
  "application": "guide-test-dev",
  "dataset": "ventes-terrain",
  "validation": {
    "valid": false,
    "errors": [{"field": "montant", "error": "Required field is missing", "row": 0}],
    "row_count": 1
  },
  "results": null,
  "insights": [],
  "ai_interpretation": null
}
```

➡️ **Votre code doit tester `success`** (et non seulement le code HTTP). La run est tracée
comme `failed` dans l'historique ; corrigez les lignes signalées puis renvoyez.

---

## 6️⃣ Étape 4 — Analyser N datasets en un seul appel (`POST /api/v1/analyze/multi`)

L'endpoint **consolidé** : plusieurs jeux de données de votre app en **une passe** —
chaque dataset garde ses propres résultats/insights/runs, et l'API ajoute une **couche
transverse** : corrélations **entre** jeux, **synthèse décisionnelle** (verdict) et une
**seule** interprétation IA lisant l'ensemble.

```bash
curl -X POST http://localhost:8000/api/v1/analyze/multi \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $ANALYTICS_API_KEY" \
  -d '{
    "application": "ma-structure",
    "datasets": ["ventes-terrain", "electricite"],
    "analysis": ["summary", "trend", "anomaly"],
    "join_key": "mois",
    "include_ai": true,
    "payloads": {
      "ventes-terrain": [
        {"mois": "2026-01", "montant": 12000},
        {"mois": "2026-02", "montant": 15500},
        {"mois": "2026-03", "montant": 14800},
        {"mois": "2026-04", "montant": 17200},
        {"mois": "2026-05", "montant": 16900},
        {"mois": "2026-06", "montant": 19500}
      ],
      "electricite": [
        {"mois": "2026-01", "montant": 420},
        {"mois": "2026-02", "montant": 460},
        {"mois": "2026-03", "montant": 440},
        {"mois": "2026-04", "montant": 470},
        {"mois": "2026-05", "montant": 455},
        {"mois": "2026-06", "montant": 480}
      ]
    }
  }'
```

### Les 6 règles de l'endpoint

| # | Règle | Sinon |
|---|---|---|
| 1 | **1 à 10 datasets**, slugs uniques, tous déclarés dans **votre** app | `422` (cap) / `404` (introuvable ou appartenant à un autre locataire) |
| 2 | Les clés de `payloads` doivent **correspondre exactement** à `datasets` | `422` — voir l'exemple réel ci-dessous |
| 3 | Chaque payload : tableau **non vide**, **≤ 10 000 lignes** | `422` |
| 4 | `join_key` = colonne commune d'alignement (`mois`, `date`…) | Sans elle : analyse OK mais **liens croisés ignorés** (jamais devinés) |
| 5 | Liens croisés : **≥ 5 lignes alignées** sur la clé, colonnes **numériques**, \|r\| ≥ 0.4 et p < 0.05 | `cross_correlations: []` |
| 6 | Si **un seul** dataset échoue la validation → `success: false`, la couche consolidée est **retenue** | cf. §5 |

**Exemple réel de `422` (payload manquant) :**

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body"],
      "msg": "Value error, missing payload(s) for: electricite",
      "input": {"application": "…", "datasets": ["ventes-terrain", "electricite"], "…": "…"}
    }
  ]
}
```

### Réponse consolidée (vraie sortie, tronquée)

```json
{
  "success": true,
  "application": "guide-test-dev",
  "datasets": ["ventes-terrain", "electricite"],
  "join_key": "mois",
  "validations": {"ventes-terrain": {"valid": true, "row_count": 6},
                  "electricite":    {"valid": true, "row_count": 6}},
  "results":  {"ventes-terrain": {"summary": ["…"], "trend": ["…"], "anomaly": ["…"]},
               "electricite":    {"summary": ["…"], "trend": ["…"], "anomaly": ["…"]}},
  "insights": {"ventes-terrain": ["…"], "electricite": ["…"]},
  "cross_correlations": [
    {"dataset1": "electricite", "column1": "montant",
     "dataset2": "ventes-terrain", "column2": "montant",
     "coefficient": 0.9546, "p_value": 0.003,
     "strength": "strong", "relationship": "positive"}
  ],
  "synthesis": {
    "datasets_analyzed": 2,
    "total_rows": 12,
    "join_key": "mois",
    "trends": {"ventes-terrain": "up", "electricite": "stable"},
    "divergent": false,
    "top_links": ["…"],
    "risks": [],
    "verdict": "positif",
    "summary": "2 jeu(x) de données analysés en une seule passe (12 lignes, alignés sur « mois »). Tendances dominantes — ventes-terrain : hausse, electricite : stable. Lien le plus fort : « montant » (electricite) et « montant » (ventes-terrain) évoluent dans le même sens (r = 0.9546). Verdict : dynamique globale positive."
  },
  "ai_interpretation": "{ \"provider\": \"groq\", \"summary\": \"…\", \"…\": \"…\" }",
  "analysis_ids": {"ventes-terrain": "6b2ce29d-…", "electricite": "…"}
}
```

**La couche consolidée :**

| Champ | Signification |
|---|---|
| `cross_correlations[]` | Liens **entre** jeux : `coefficient` (r), `p_value`, `strength` (`strong` si \|r\| ≥ 0.7, sinon `moderate`), `relationship` (`positive` = même sens / `negative` = sens inverse). Triés du plus fort au plus faible, max 20 |
| `synthesis.verdict` | `positif` 🟢 · `equilibre` 🔵 · `tension` 🟡 · `surveiller` 🔴 (un risque bat une divergence, qui bat une tendance) |
| `synthesis.divergent` | `true` si des jeux montent **et** d'autres descendent |
| `synthesis.risks` | Alertes d'anomalies par jeu |
| `synthesis.summary` | Phrase de synthèse prête à afficher (FR) |
| `analysis_ids` | **Une run par dataset** (l'historique reste par jeu) |

---

## 7️⃣ Étape 5 — Relire l'historique et les insights

Tout ce que vous analyse est persisté — vous pouvez le relire **plus tard, avec la même clé** :

```bash
# Dernières runs de VOTRE application (?limit=1..200 défaut 50, ?skip=0 défaut 0)
curl -H "X-API-Key: $ANALYTICS_API_KEY" \
  "http://localhost:8000/api/v1/analysis?limit=2"

# Page suivante : on saute les N premières (rangées les plus récentes d'abord)
curl -H "X-API-Key: $ANALYTICS_API_KEY" \
  "http://localhost:8000/api/v1/analysis?limit=2&skip=2"
# Page vide = fin de l'historique (200, [] — pas une erreur)
```

```json
[{
  "id": "6b2ce29d-f176-46bc-8951-a7b5ace96f84",
  "application_id": "ffff7a62-42e4-42c8-ac98-1a9429098b2c",
  "dataset_id": "90d3c38e-07a1-41cb-9a69-73ceb0f723bf",
  "analysis_types": "summary,trend,anomaly",
  "status": "completed",
  "row_count": 6,
  "error_message": null,
  "created_at": "2026-10-15T08:37:46.236339Z",
  "completed_at": "2026-10-15T08:37:46.280740Z"
}]
```

```bash
# Détail d'une run (résultats + insights + IA)
curl -H "X-API-Key: $ANALYTICS_API_KEY" \
  "http://localhost:8000/api/v1/analysis/6b2ce29d-f176-46bc-8951-a7b5ace96f84"

# Insights seuls — tous (?limit=1..200) ou ceux d'une run (?run_id=…)
curl -H "X-API-Key: $ANALYTICS_API_KEY" \
  "http://localhost:8000/api/v1/insights?run_id=6b2ce29d-…&limit=50"
```

**Réelle réponse `/insights`** :

```json
[{
  "id": "00c196a7-e85e-40bd-9d06-e6475c85a255",
  "type": "trend",
  "severity": "low",
  "title": "Stabilité sur montant",
  "description": "L'indicateur montant demeure constant sur 6 périodes (variation de 14.3%). Aucune rupture d'activité.",
  "metric": "montant",
  "value": 14.29,
  "unit": "%",
  "confidence": 0.6
}]
```

> 🔒 `status` d'une run : `running` → `completed` | `failed` (`error_message` renseigné).
> Une run ou insight **d'une autre application** répond `404` (pas `403`) — l'existence
> de ressources tierces ne se révèle jamais.

---

## 8️⃣ Catalogue complet des endpoints

**Légende auth** : 🔑 = `X-API-Key` · 🎫 = JWT dashboard · 🌐 = publique

| Méthode | Chemin | Auth | Limite | Retour |
|---|---|---|---|---|
| GET | `/api/v1/health` | 🌐 | — | santé (base, provider IA) |
| POST | `/api/v1/applications` | 🌐 | 15/min | `201` profil + **clé une fois** |
| GET | `/api/v1/applications` | 🔑 | — | ma seule application |
| GET/PUT/DELETE | `/api/v1/applications/me` | 🔑 | — | profil / maj / `204` |
| POST | `/api/v1/applications/me/regenerate-key` | 🔑 | — | nouvelle clé (une fois) |
| POST | `/api/v1/applications/me/revoke-key` | 🔑 | — | `204` |
| GET | `/api/v1/applications/{app_id}` | 🔑 | — | profil (si propriétaire) |
| POST | `/api/v1/applications/{app_id}/regenerate-key` | 🔑 | — | nouvelle clé |
| DELETE | `/api/v1/applications/{app_id}` | 🔑 | — | `204` |
| GET | `/api/v1/applications/admin/all` | 🎫 | — | toutes les apps (dashboard) |
| POST | `/api/v1/applications/admin/{app_id}/regenerate-key` | 🎫 | — | clé d'un locataire |
| DELETE | `/api/v1/applications/admin/{app_id}` | 🎫 | — | `204` |
| POST | `/api/v1/datasets` | 🔑 | 30/min | `201` dataset |
| GET | `/api/v1/datasets?skip=0&limit=100` | 🔑 | — | mes datasets (skip ≥ 0, limit 1–500) |
| GET | `/api/v1/datasets/{dataset_id}` | 🔑 | — | dataset |
| PUT | `/api/v1/datasets/{dataset_id}` | 🔑 | — | dataset modifié |
| DELETE | `/api/v1/datasets/{dataset_id}` | 🔑 | — | `204` |
| GET | `/api/v1/datasets/all` | 🎫 | — | tous les datasets (dashboard) |
| GET | `/api/v1/datasets/by-app/{app_slug}` | 🎫 | — | datasets d'un locataire |
| POST | `/api/v1/analyze` | 🔑 | **20/min** | `200` AnalyseResponse |
| POST | `/api/v1/analyze/multi` | 🔑 | **10/min** | `200` MultiAnalysisResponse |
| POST | `/api/v1/analyze/quick` | 🌐 | 30/min | banc d'essai — **pas pour la prod** |
| GET | `/api/v1/analysis?limit=` | 🔑 | — | runs (limit 1–200, déf. 50) |
| GET | `/api/v1/analysis/{run_id}` | 🔑 | — | détail d'une run |
| GET | `/api/v1/insights?run_id=&limit=` | 🔑 | — | insights (limit ≤ 200, déf. 50) |
| POST | `/api/v1/auth/login` | 🌐 | 5/min | ticket JWT dashboard (12 h) |
| GET | `/api/v1/auth/me` | 🎫 | — | utilisateur connecté |

**Le banc d'essai rapide** (utile pour tester le moteur sans rien déclarer) :

```bash
curl -X POST http://localhost:8000/api/v1/analyze/quick \
  -H "Content-Type: application/json" \
  -d '{"data": [{"valeur": 120, "score": 4.5}, {"valeur": 140, "score": 4.8}],
       "analysis": ["summary"], "label": "test"}'
```

```json
{"success": true, "label": "test", "row_count": 3,
 "fields_inferred": [{"name": "score", "technical_type": "float", "…": "…"},
                     {"name": "valeur", "technical_type": "integer", "…": "…"}],
 "results": {"summary": ["…"]}, "insights": ["…"], "ai_interpretation": null}
```

*(Les types sont inférés automatiquement — `score:float`, `valeur:integer`.)*

---

## 9️⃣ Codes d'erreur & gestion côté client

| Code | Déclencheur | Corps (vraies sorties) | Que faire ? |
|---|---|---|---|
| `401` | En-tête absent | `{"detail":"Missing X-API-Key header"}` | Ajouter `X-API-Key` à la requête |
| `401` | Clé fausse / révoquée | `{"detail":"Invalid or revoked API key"}` | Vérifier la variable d'env ; régénérer si fuite |
| `403` | Clé d'une app, `application` d'une autre | `{"detail":"API key does not match the requested application"}` | Utiliser le slug de **votre** app |
| `404` | App ou dataset inconnu / chez un autre locataire | `{"detail":"Dataset not found"}` | Vérifier le slug (`GET /datasets`) |
| `404` | Run / insight qui n'appartient pas à votre app | `{"detail":"Analysis run not found"}` | Idem — isolation |
| `422` | Corps invalide, payloads ≠ datasets, cap dépassé | `{"detail":[{"type":"value_error","loc":["body"],"msg":"Value error, missing payload(s) for: …"}]}` | Lire `detail[].msg` |
| `429` | Quota dépassé (cf. §10) | `{"error":"Rate limit exceeded: …"}` | Patienter (fenêtre glissante d'1 min) |
| `200` + `success:false` | Données non conformes au schéma | `validation.errors[]` | Corriger les lignes, renvoyer (§5) |

> Les erreurs `4xx` sont **vôtres** (requête) ; une `5xx` est **à remonter** à l'opérateur de l'API.

### Exemple JavaScript (backend Node / edge functions)

```js
const BASE = process.env.ANALYTICS_API_URL || "http://localhost:8000";
const KEY  = process.env.ANALYTICS_API_KEY; // jamais côté navigateur !

export async function analyserVentes(lignes) {
  const res = await fetch(`${BASE}/api/v1/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-API-Key": KEY },
    body: JSON.stringify({
      application: "ma-structure",
      dataset: "ventes-terrain",
      analysis: ["summary", "trend", "anomaly"],
      include_ai: true,
      data: lignes,
    }),
  });

  if (res.status === 429) {
    // fenêtre glissante : réessayer après 60 s
    await new Promise((r) => setTimeout(r, 60_000));
    return analyserVentes(lignes);
  }
  if (!res.ok) {
    const { detail } = await res.json().catch(() => ({}));
    throw new Error(`Analyse refusée (${res.status}) : ${JSON.stringify(detail)}`);
  }

  const out = await res.json();
  if (!out.success) {
    // 200 mais schéma non respecté → detail exploitable ligne par ligne
    console.error("Lignes invalides :", out.validation.errors);
    return { ok: false, erreurs: out.validation.errors };
  }

  const ia = out.ai_interpretation ? JSON.parse(out.ai_interpretation) : null;
  return { ok: true, insights: out.insights, ia, synthese: out.results.summary };
}
```

### Exemple Python

```python
import json, os, time, requests

BASE = os.getenv("ANALYTICS_API_URL", "http://localhost:8000")
KEY = os.getenv("ANALYTICS_API_KEY")  # jamais dans le front !
H = {"X-API-Key": KEY, "Content-Type": "application/json"}

def analyser(application: str, dataset: str, lignes: list[dict]) -> dict:
    r = requests.post(f"{BASE}/api/v1/analyze", headers=H, json={
        "application": application,
        "dataset": dataset,
        "analysis": ["summary", "trend", "anomaly"],
        "include_ai": True,
        "data": lignes,
    }, timeout=60)

    if r.status_code == 429:
        time.sleep(60)
        return analyser(application, dataset, lignes)          # retry simple
    if r.status_code >= 400:
        raise RuntimeError(f"API {r.status_code} : {r.json().get('detail')}")

    out = r.json()
    if not out["success"]:                                     # schéma non respecté
        return {"ok": False, "erreurs": out["validation"]["errors"]}

    ia = json.loads(out["ai_interpretation"]) if out["ai_interpretation"] else None
    return {"ok": True, "insights": out["insights"], "ia": ia}
```

---

## 🔟 Limites & quotas

| Limite | Valeur | Paramètre / endpoint concerné |
|---|---|---|
| Lignes par requête | **10 000** | `data[]` (`/analyze`), chaque payload (`/analyze/multi`) |
| Datasets par analyse consolidée | **10** | `/analyze/multi` → `datasets[]` (min 1, uniques) |
| Liens croisés retournés | **20** (max) | `cross_correlations[]`, triés par \|r\| |
| Lignes minimales alignées pour un lien | **5** | `join_key` |
| Appels `POST /applications` | **15/min** | fenêtre glissante 1 min |
| Appels `POST /datasets` | **30/min** | idem |
| Appels `POST /analyze` | **20/min** | idem |
| Appels `POST /analyze/multi` | **10/min** | réglable via `ANALYZE_MULTI_PER_MINUTE` |
| Appels `POST /analyze/quick` | **30/min** | idem |
| Login dashboard | **5/min** | `DASHBOARD_LOGIN_PER_MINUTE` |
| Pagination `GET /datasets` | `limit` 1–500 (déf. 100), `skip` ≥ 0 | au-delà : `400` |
| Pagination `GET /analysis`, `/insights` | `limit` 1–200 (déf. 50) | au-delà : `422` |

- Le **compteur est par clé API** (chaque locataire a son propre quota), ou par IP si pas de clé.
- Une fenêtre d'1 minute : après le quota, réessayez **< 60 s** plus tard.

---

## 1️⃣1️⃣ Sécurité — les 5 règles

1. **La clé reste côté serveur** (`.env`, coffre, variable d'infra). Un bundle frontend est public.
2. **Toujours HTTPS en production** (Railway le termine déjà).
3. **Jamais de clé dans un log, une URL (`?key=`), ni un commit.**
4. **Clé fuite = `POST /applications/me/regenerate-key`** (l'ancienne meurt immédiatement).
5. Les **lignes brutes ne partent jamais vers l'IA** — seuls des agrégats anonymisés (cf. `AnalyticalContext`).

---

## 1️⃣2️⃣ Dépannage (FAQ)

| Symptôme | Cause la plus fréquente | Solution |
|---|---|---|
| `401 Missing X-API-Key header` | En-tête oublié ou nommé autrement | Le nom est **exactement** `X-API-Key` |
| `401 Invalid or revoked API key` | Mauvaise clé / régénérée / fausse env | Relire `.env`, sinon régénérer |
| `403 API key does not match…` | `application` = slug d'une **autre** app | Utiliser **votre** slug (`GET /applications/me` → `slug`) |
| `404 Dataset not found` | Slug absent (ou chez un autre locataire) | `GET /api/v1/datasets` list vos slugs |
| `422 missing payload(s) for: X` | `payloads` ≠ `datasets` (§6 règle 2) | Clés **identiques**, mot pour mot |
| `200 success:false` + `validation.errors` | Ligne sans colonne `required` / mauvais type | Corriger d'après `field` + `row` |
| `429 Rate limit exceeded` | Trop d'appels en 1 min | Retry après la fenêtre (§10) |
| `cross_correlations: []` | (a) pas de `join_key` · (b) < 5 lignes alignées · (c) colonnes non numériques | Vérifier les3 points — la `synthesis.summary` le signale |
| `ai_interpretation: null` | `include_ai: false`, **ou** provider IA en panne | Mettre `true` ; vérifier `GET /health` → `ai_provider` |
| Réponse JSON illisible / `Expecting property name` sous PowerShell | PowerShell mange les guillemets du `-d '{…}'` | Écrire le corps dans un fichier : `-d "@payload.json"` |
| Dashboard : sélecteur de datasets vide | App sans dataset déclaré | Déclarer via `POST /datasets` (§4) |
| Run bloquée `running` / `failed` | Crash en cours de post-traitement | `error_message` sur `GET /analysis/{id}` ; relancer |

---

## A️⃣ Annexe — scripts complets

### Python : parcours complet (création → analyse → historique)

```python
"""Démo complète de l'intégration T-ola — à lancer une fois."""
import json, os, requests

BASE = os.getenv("ANALYTICS_API_URL", "http://localhost:8000")
s = requests.Session()

# 1) Créer l'application (une seule fois) → CLÉ AFFICHÉE UNE FOIS
app = s.post(f"{BASE}/api/v1/applications",
             json={"name": "Ma Structure"}, timeout=30).json()
key = app["api_key"]
s.headers.update({"X-API-Key": key, "Content-Type": "application/json"})
print("Clé (à stocker en env) :", key[:12] + "…")

# 2) Déclarer le dataset
s.post(f"{BASE}/api/v1/datasets", json={
    "name": "Ventes terrain", "slug": "ventes-terrain",
    "fields": [
        {"name": "mois", "type": "string", "required": True},
        {"name": "montant", "type": "float", "required": True},
    ],
}, timeout=30).raise_for_status()

# 3) Analyser
resp = s.post(f"{BASE}/api/v1/analyze", json={
    "application": app["slug"], "dataset": "ventes-terrain",
    "analysis": ["summary", "trend", "anomaly"], "include_ai": True,
    "data": [{"mois": f"2026-{m:02d}", "montant": v} for m, v in
             zip(range(1, 7), [12000, 15500, 14800, 17200, 16900, 19500])],
}, timeout=60).json()
print("Succès :", resp["success"], "| Insights :", len(resp["insights"]))
if resp["ai_interpretation"]:
    print("IA :", json.loads(resp["ai_interpretation"])["summary"])

# 4) Historique
runs = s.get(f"{BASE}/api/v1/analysis", params={"limit": 5}, timeout=30).json()
print("Runs :", [(r["status"], r["row_count"]) for r in runs])
```

### Node : multi-analyse consolidée

```js
const BASE = process.env.ANALYTICS_API_URL || "http://localhost:8000";
const KEY = process.env.ANALYTICS_API_KEY;

const res = await fetch(`${BASE}/api/v1/analyze/multi`, {
  method: "POST",
  headers: { "Content-Type": "application/json", "X-API-Key": KEY },
  body: JSON.stringify({
    application: "ma-structure",
    datasets: ["ventes-terrain", "electricite"],
    analysis: ["summary", "trend", "anomaly"],
    join_key: "mois",
    include_ai: true,
    payloads: {
      "ventes-terrain": [/* lignes… */],
      "electricite":    [/* lignes… */],
    },
  }),
});
const out = await res.json();
if (out.success) {
  console.log("Verdict :", out.synthesis.verdict);
  console.log("Synthèse :", out.synthesis.summary);
  console.log("Liens :", out.cross_correlations);
}
```

---

> 🧭 **Aller plus loin** : référence exhaustive des champs et des types → [`api.md`](api.md) ·
> Screens & modèle métier → [`EXECUTIVE_PROJECT_PRESENTATION.md`](EXECUTIVE_PROJECT_PRESENTATION.md) ·
> Commandes utiles → [`../COMMANDES.md`](../COMMANDES.md)
