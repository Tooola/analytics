# 🔬 Diagnostic Complet — Open Analytics AI
> Audit réalisé le 12/10/2026 — Pour présentation ce soir.

---

## 🔴 Problèmes Critiques Identifiés (Bloquants)

### Bug #1 — `post` non importé dans `views/analytics.py`

**Symptôme :** "Cannot reach API" ou crash silencieux au clic "Lancer l'analyse".

**Cause :** La vue `analytics.py` importe `_post` (alias privé) depuis `api_client` mais appelle `post(...)` sans underscore aux lignes 143 et 95 (`ai_playground.py` aussi).  
Le nom `post` n'est jamais importé → `NameError` au runtime Streamlit = la page plante de manière imprévisible.

```python
# Ce qui est importé (ligne 31) :
from api_client import post as _post   # ← alias _post

# Ce qui est appelé (ligne 143) :
r = post("/api/v1/analyze", ...)       # ← NameError : 'post' not defined
```

**Fix (1 ligne) :** Changer l'import `post as _post` → `post` (sans alias), ou remplacer l'appel `post(` par `_post(`.  
➡️ **Même bug dans `views/ai_playground.py` ligne 95.**

---

### Bug #2 — Groq AI tombe systématiquement sur MockProvider

**Symptôme :** Dashboard affiche "mock" comme provider, jamais de vraie interprétation.

**Cause :** Le `.env` local a `AI_PROVIDER=groq` et une clé `GROQ_API_KEY=gsk_...` mais en **production Railway**, ces variables ne sont probablement pas injectées.  
→ `settings.groq_api_key` est `None` → `engine.py:37-42` bascule sur `MockAIProvider`.

**Vérification rapide :** Sur Railway → Settings → Variables → vérifier que `AI_PROVIDER=groq` ET `GROQ_API_KEY=gsk_lYCr3...` sont bien présentes.

> ⚠️ La clé dans le `.env` local (`gsk_lYCr3tBSkHK...`) est **exposée dans les fichiers versionnés** — elle doit être révoquée sur console.groq.com et régénérée directement dans Railway Variables.

---

### Bug #3 — Dashboard instable : connexion API aléatoire

**Causes multiples :**
1. Le `api_client.get()` / `post()` utilise `get_api_base()` qui lit `st.session_state["api_base"]` — mais sur **Streamlit Cloud**, le `session_state` est réinitialisé à chaque "cold start" du pod.
2. `st.secrets` n'a pas de clé `api_base_url` configurée → fallback sur la Railway URL hard-codée `scintillating-kindness-production-d038.up.railway.app`.
3. Le dashboard Streamlit Cloud (`analytics-juyrngykeyfzfv9jtfg3st.streamlit.app`) fait des appels à Railway backend — si Railway s'est mis en veille (cold start ~5s), le timeout de 5s du health check expire → la sidebar affiche "🔴 Offline" alors que le backend est juste lent.

**Fix immédiat :** Dans le dashboard Streamlit Cloud → Settings → Secrets, ajouter :
```toml
api_base_url = "https://scintillating-kindness-production-d038.up.railway.app"
```

**Fix timeout :** Dans `api_client.py`, augmenter le timeout du health check de `5s → 15s`.

---

### Bug #4 — Insights trop techniques, pas Business-Analyst

**Symptôme :** Les insights retournés sont en anglais, avec du jargon statistique ("zscore", "ensemble (iqr + mad + isolation_forest)"), pas adaptés à un décideur.

**Cause :** `insights/engine.py` génère des textes hardcodés en anglais technique. Exemples :
- `"1 anomaly/anomalies detected in yield_kg"` 
- `"yield_kg: count=8, mean=5056.25, median=4575.0..."`

Ces insights sont aussi passés à Groq comme contexte — si Groq ne fonctionne pas (Bug #2), c'est tout ce que l'utilisateur voit.

---

### Bug #5 — Tests: état à vérifier

Les tests font probablement timeout ou ont des imports ratés. En attente du résultat de la commande lancée.

---

## ✅ Ce qui FONCTIONNE bien

| Composant | État |
|---|---|
| Architecture FastAPI | ✅ Solide, bien structurée |
| Validation des données | ✅ Fonctionne |
| Anomaly detection (IQR + MAD + IForest) | ✅ Bien implémenté |
| Trend & Forecast analysis | ✅ OK |
| Groq provider (le code lui-même) | ✅ Correct — problème = variables d'env |
| BI Report component (bi_report.py) | ✅ Beau rendu, bien fait |
| Sécurité (rate-limit, API key auth) | ✅ Correct |

---

## 🚑 PLAN D'ACTION — Ce Soir (Urgent)

### Phase 1 — Fixes bloquants (< 30 min)

#### Fix A : Corriger l'import `post` dans les deux vues

**Fichier :** `dashboard/views/analytics.py` (ligne 28-31)
```python
# AVANT
from api_client import get as _get
from api_client import get_api_base as _get_api_base
from api_client import post as _post

# APRÈS
from api_client import get as _get
from api_client import get_api_base as _get_api_base
from api_client import post  # ← sans alias
```
Et à la ligne 143, `post(` au lieu de `_post(` si tu gardes l'alias.

**Même correction dans `dashboard/views/ai_playground.py`** ligne 19-21.

#### Fix B : Variables Railway — Groq doit marcher

Sur [railway.app](https://railway.app) → ton service backend → Variables :
```
AI_PROVIDER=groq
GROQ_API_KEY=<nouvelle_clé_générée_sur_console.groq.com>
```
> ⚠️ Révoque d'abord l'ancienne clé sur console.groq.com (elle est exposée dans le .env commité).

#### Fix C : Secrets Streamlit Cloud — fin du "Offline" aléatoire

Sur [share.streamlit.io](https://share.streamlit.io) → ton app → Settings → Secrets :
```toml
api_base_url = "https://scintillating-kindness-production-d038.up.railway.app"
```

#### Fix D : Health check timeout — sidebar stable

Dans `dashboard/api_client.py`, ligne 129 :
```python
# AVANT
timeout=5,
# APRÈS  
timeout=15,
```

---

### Phase 2 — Insights Business-Friendly (< 2h)

Réécrire `insights/engine.py` pour produire des textes en **français**, orientés **décideur**, pas statisticien.

**Avant :** `"1 anomaly/anomalies detected in yield_kg"`  
**Après :** `"⚠️ Valeur atypique détectée sur le rendement (yield_kg) : 1 enregistrement dépasse significativement la norme."`

**Avant :** `"yield_kg increased by 6.67%"`  
**Après :** `"📈 Le rendement (yield_kg) est en hausse de +6.67% — tendance favorable confirmée."`

---

### Phase 3 — Test sans Dataset préalable (angle admin dashboard)

**Idée :** Ajouter un mode "Quick Test" dans la page **Analytics** ou **Playground** qui :
1. Accepte un JSON brut + détecte automatiquement les colonnes (types auto-inférés)
2. Crée une app temporaire + dataset "on-the-fly" en interne (sans passer par le UI Applications/Datasets)
3. Envoie à `/api/v1/analyze` et affiche le rapport

**Alternative plus simple :** Ajouter un endpoint backend `POST /api/v1/analyze/quick` qui accepte le JSON **sans** `application` ni `dataset` requis — il génère les champs depuis les données reçues.

---

## 🗺️ Perspective React Dashboard

### Pourquoi c'est une bonne idée

| Streamlit | React |
|---|---|
| Rechargements intempestifs | Rendu contrôlé, stable |
| Session state instable en cloud | localStorage / context stables |
| Difficile à customiser visuellement | Contrôle total du UI |
| Pas fait pour être un vrai dashboard | Fait pour ça |

### Architecture recommandée

```
React SPA (Vite + Tailwind)
    │
    ├── Page: Dashboard Overview (KPIs globaux)
    ├── Page: Run Analysis (paste JSON → résultats en live)  ← priorité 1
    ├── Page: Applications Manager
    ├── Page: Datasets Manager
    └── Page: Analysis History
    │
    ▼ calls
FastAPI Backend (inchangé — la valeur du projet)
```

**Le backend NE CHANGE PAS.** C'est lui qui fait le vrai travail. Le dashboard React est juste une interface de visualisation.

### Coût estimé

- Dashboard React minimal (Run Analysis + Overview) : **~4-6h** de dev
- Remplacement complet Streamlit → React : **~1-2 jours**

---

## 📋 Résumé Exécutif

| Problème | Sévérité | Temps fix | Impact |
|---|---|---|---|
| `post` non importé → crash analyse | 🔴 Critique | 2 min | Pages analytics/playground cassées |
| Groq → Mock (Railway vars manquantes) | 🔴 Critique | 5 min | 0% d'IA réelle |
| Dashboard "Offline" intermittent | 🟠 Élevé | 5 min | Présentation instable |
| Insights en anglais technique | 🟡 Moyen | 2h | Mauvaise impression |
| Tests à vérifier | 🟡 Moyen | TBD | CI/stabilité |

**Pour ce soir :** Fix A + B + C + D = ~15 min → Groq fonctionne + dashboard stable.
