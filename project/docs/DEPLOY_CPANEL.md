# 🖥️ Déployer T-ola sur un serveur cPanel

> **Réponse courte : OUI, c'est possible** — à condition que votre hébergeur propose
> l'une de ces deux tuiles dans la cPanel : **« Setup Python App »** (recommandé) ou
> **« Setup Node.js App »**. La vérification prend 10 secondes : ouvrez la cPanel,
> cherchez « Application » dans la section **Software**.
>
> Ce guide suppose « Setup Python App ». Si votre cPanel ne l'a pas, voir
> [§9 — Fallbacks](#9--fallbacks--si-votre-chepanel-na-pas-python-app).

---

##0. Pourquoi c'est possible « naturellement » — le dépôt est déjà prêt

| Brique | État dans le dépôt | Conséquence cPanel |
|---|---|---|
| **Base de données** | SQLite **par défaut** (`sqlite:///./analytics.db` dans `config.py`) | **Aucune base à créer** — le fichier se génère au premier démarrage |
| **Création du schéma** | `Base.metadata.create_all` au démarrage + seed admin depuis l'env | Premier lancement = base + tables + compte admin, tout seul |
| **Dépendances** | `requirements.txt` épinglé (bains précompilés) | `pip install` fonctionne sur tout hébergement partagé |
| **Entrée WSGI** | `wsgi.py` (pont ASGI→WSGI via `a2wsgi`) | Passerelle Passenger/cPanel assurée |
| **Front** | Vite → dossier `dist/` statique + `VITE_API_URL` au build | Se dépose tel quel dans `public_html/` |
| **Secrets** | Zéro secret en dur, tout en variables d'env | Se configure dans l'UI cPanel, jamais dans les fichiers |

---

##1. L'architecture cible

```
        https://domaine.com                    https://api.domaine.com
        (statique Apache)                      (Passenger — FastAPI)
┌───────────────────────────┐          ┌──────────────────────────────────┐
│ public_html/              │  HTTPS   │ /home/CPUSER/analytics-api/      │
│ ├── index.html            │ ───────► │ ├── app/            (code)       │
│ ├── assets/*.js,*.css     │  appel   │ ├── wsgi.py         (entrée)     │
│ └── .htaccess (SPA)       │  API     │ ├── requirements.txt             │
└───────────────────────────┘          │ ├── analytics.db    (SQLite, auto)│
                                       │ └── .virtualenvs/   (pip auto)   │
                                       └──────────────────────────────────┘
```

**Règles d'or :**
1. Le **code API** vit **hors** de `public_html/` (jamais de code accessible publiquement).
2. Le **`.env`** n'est **jamais** uploadé : les variables se posent dans l'UI cPanel.
3. Le front et l'API parlent via **deux noms de domaine** (site + sous-domaine `api.`).

**Arborescence côté serveur :**

```
/home/CPUSER/
├── public_html/                  ← front React (build statique)
│   ├── index.html
│   ├── assets/
│   └── .htaccess                 ← fallback SPA (404 → index.html)
└── analytics-api/                ← backend FastAPI (HORS public_html)
    ├── app/
    ├── wsgi.py
    ├── requirements.txt
    └── analytics.db              ← créé au 1er démarrage (SQLite)
```

---

##2. Étape 1 — Préparer les deux artefacts (chez vous)

### a) Le front : build statique pointant sur l'API

```bash
cd project/frontend
VITE_API_URL=https://api.domaine.com npm run build   # PowerShell : $env:VITE_API_URL="https://api.domaine.com"; npm run build
```

→ vous obtenez `dist/` (index.html + assets/). **`VITE_API_URL` est gravée dans le
build** : c'est l'adresse que le navigateur appellera.

> 💡 Si l'URL de build était fausse : le dashboard permet déjà de corriger l'API base
> côté client (stockage local `oak_api_base`), mais faites les choses bien au build.

### b) Le backend : archive SANS les inutiles

Depuis `project/backend/`, archivez **uniquement** : `app/`, `wsgi.py`,
`requirements.txt`, `alembic/`. **Exclure** : `.venv/`, `__pycache__/`, `analytics.db`,
`.env`, `tests/`.

---

##3. Étape 2 — Créer l'application Python dans cPanel

**cPanel → Software → Setup Python App → Create Application** :

| Champ cPanel | Valeur à entrer |
|---|---|
| **Python version** | 3.11 ou 3.12 (le plus récent proposé) |
| **Application root** | `/home/CPUSER/analytics-api` (crée le dossier) |
| **Application URL** | le sous-domaine `api.domaine.com` (créez-le d'abord dans *Domains* si besoin) |
| **Application startup file** | `wsgi.py` |
| **Passenger log file** | défaut (`tmp/errors.log` dans l'application root) |

🎬 **Save** — cPanel crée le virtualenv et prépare le démarrage.

---

##4. Étape 3 — Uploader le code

Trois voies au choix (même résultat) :

| Voie | Comment |
|---|---|
| **File Manager** | cPanel → File Manager → dans `analytics-api/` → Upload → le `.zip` → *Extract* |
| **SSH** (si dispo) | `scp backend.zip CPUSER@serv:/home/CPUSER/analytics-api/` puis `unzip` |
| **Git** (si le host le propose) | Dépôt privé + pull dans `analytics-api/` |

Vérifiez la présence de `wsgi.py`, `app/`, `requirements.txt` **à la racine** de
`analytics-api/`.

---

##5. Étape 4 — Installer les dépendances

**Option A (UI)** : retournez dans *Setup Python App* → bouton **« Run Script »** /
le champ d'exécution automatique : cPanel exécute `pip install -r requirements.txt`
**à chaque Save** — un simple *Save* suffit souvent.

**Option B (Terminal cPanel)** :

```bash
cd ~/analytics-api
~/.virtualenvs/analytics-api/bin/pip install -r requirements.txt
```

⏱️ Premier install : **5 à15 min** (pandas/scipy/scikit-learn ≈ 400-600 Mo au total —
vérifiez votre quota disque dans cPanel → *Quotas*).

---

##6. Étape 5 — Les variables d'environnement (l'UI cPanel « Environment Variables »)

⚠️ **`extra=forbid`** : le backend **refuse de démarrer** si une clé inconnue traîne —
ne déclarez **que** les lignes ci-dessous.

| Variable | Valeur | Obligatoire ? |
|---|---|---|
| `APP_ENV` | `production` | ✅ |
| `API_KEY_HASH_SECRET` | une phrase longue et aléatoire (≥ 32 car.) | ✅ obligatoire en prod (le code refuse le défaut) |
| `DASHBOARD_ADMIN_USERNAME` | ex. `admin` | ✅ pour le login dashboard |
| `DASHBOARD_ADMIN_PASSWORD` | mot de passe fort | ✅ idem |
| `AI_PROVIDER` | `groq` | ✅ |
| `GROQ_API_KEY` | votre clé Groq | ✅ si provider groq |
| `CORS_ORIGINS` | `["https://domaine.com"]` | ✅ — **format JSON**, liste des origines du front |
| `DATABASE_URL` | *(ne pas mettre)* | Par défaut SQLite — ne rien déclarer |
| `ANALYZE_MULTI_PER_MINENTE`… | *(ne pas mettre)* | Quotas : valeurs par défaut correctes |

🎬 **Restart** l'application dans l'UI cPanel.

---

##7. Étape 6 — Vérifier l'API en live

Depuis n'importe quel poste :

```bash
curl https://api.domaine.com/api/v1/health
```

```json
{"status":"healthy","version":"1.0.0","database":"connected","ai_provider":"groq","...":"..."}
```

Puis connectez-vous au dashboard (`https://api.domaine.com/docs` répond aussi —
Swagger public : c'est voulu, la donnée reste derrière les clés).

**Si ça ne démarre pas** : *Setup Python App → Error log* (le plus souvent : variable
manquante, ou typo de clé → message `extra=forbid`).

---

##8. Étape 7 — Déposer le front + HTTPS

1. **File Manager → `public_html/`** → Upload → extraitez le contenu de `dist/`
   (index.html + dossier assets/ **à la racine** de public_html).
2. **`.htaccess` SPA** — même dossier `public_html/`, fichier `.htaccess` :

```apache
RewriteEngine On
# Ne pas réécrire les vrais fichiers (assets Vite)
RewriteCond %{REQUEST_FILENAME} -f [OR]
RewriteCond %{REQUEST_FILENAME} -d
RewriteRule ^ - [L]
# Toute autre route → index.html (React Router)
RewriteRule ^ index.html [L]

# Sécurité minimale
<IfModule mod_headers.c>
  Header always set X-Content-Type-Options "nosniff"
</IfModule>
```

3. **HTTPS** : cPanel → *SSL/TLS Status* → **Let's Encrypt** sur `domaine.com`
   **et** `api.domaine.com` → *Install*. Le front appelle alors `https://api.…`
   sans blocage navigateur.

---

##9. Fallbacks — si votre cPanel n'a PAS Python App

| Situation | Solution |
|---|---|
| **« Setup Node.js App »** présent | Créez l'app Node (Application root identique), puis dans le terminal : `npx pipenv run pip install -r requirements.txt`… **ou** plus simple : `child_process` — non : la voie propre est de lancer `venv/bin/uvicorn app.main:app --bind 127.0.0.1:$PORT` via le champ *Application Startup File* personnalisé si votre cPanel le permet |
| **Aucun gestionnaire d'apps** | L'hébergement partagé « statique pur » **ne peut pas** faire tourner FastAPI → il faut un **VPS** (DigitalOcean, OVH VPS, Contabo —5 €/mois) où Docker ou uvicorn tournent librement, cPanel y étant optionnel |
| **PostgreSQL proposé dans cPanel** (tuile *PostgreSQL Databases*) | Facultatif mais plus solide en production : créez la base + utilisateur, puis `DATABASE_URL=postgresql+psycopg2://USER:PASS@localhost/DBNAME`. SQLite convient pour un pilote |

---

##10. Pièges cPanel — le tableau des pièges

| Piège | Symptôme | Solution |
|---|---|---|
| Code dans `public_html` | `http://domaine.com/app/config.py` expose le code | API **hors** public_html, toujours |
| `.env` uploadé | Fichier de secrets accessible/en conflit | Variables **uniquement** dans l'UI cPanel |
| Clé inconnue dans l'env | Démarrage refusé : `extra="forbid"` | Ne déclarer que les clés du §6 |
| SQLite non inscriptible | `unable to open database file` au 1er appel | `chmod 644 analytics.db` / dossier app en écriture |
| Port en dur dans un bind | App muette | Passenger injecte le port — `wsgi.py` s'en charge |
| Mixte HTTPS/HTTP | Le navigateur bloque les appels API | Let's Encrypt sur **les deux** domaines, front en `https://` |
| Quota disque | pip échoue à mi-install | Vérifier *Quotas* — prévoir ≈1 Go |
| `VITE_API_URL` oubliée au build | Dashboard cherche `127.0.0.1:8000` | Rebuild avec la variable (§2a) |
| Reload sans prévenir | Rides possibles sur SQLite léger | Acceptable pour un pilote ; migrer sur PG pour la prod réelle |

---

##11. Checklist de recette (après push)

```
□ curl https://api.domaine.com/api/v1/health → "healthy", "ai_provider": "groq"
□ https://domaine.com → page de login du dashboard
□ Login admin OK (compte seedé via env)
□ Démo multi (ventes-terrain + electricite, join_key=mois) → verdict + liens
□ https://api.domaine.com/docs → Swagger répond
□ Aucun .env ni analytics.db visible depuis le navigateur
□ CORS : le front appelle bien api.domaine.com (console navigateur = 0 erreur)
```

---

##12. Rollback

- **cPanel → Setup Python App → Restart** redémarre proprement (base SQLite intacte).
- Code en erreur : remettre l'archive précédente (File Manager), Save → Restart.
- **Sauvegarde** : cPanel → *Backup* ou simple `zip` de `analytics-api/` (la base tient
  dans `analytics.db` — un fichier).

---

> 🧭 **Références** : guide d'intégration dev [`GUIDE_INTEGRATION_DEV.md`](GUIDE_INTEGRATION_DEV.md) ·
> script de présentation [`PRESENTATION_DG.md`](PRESENTATION_DG.md) ·
> déploiement Railway [`RAILWAY_ET_KIT_COLLEGUES.md`](RAILWAY_ET_KIT_COLLEGUES.md)
