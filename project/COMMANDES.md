# 🚀 Commandes de lancement — Open Analytics AI

Ce document regroupe l'ensemble des commandes pour démarrer, tester et configurer **Open Analytics AI** (Backend FastAPI + Dashboard Admin Streamlit).

---

## ⚡ Méthode 1 : Démarrage rapide avec Docker Compose (Recommandé)

Cette méthode lance automatiquement PostgreSQL, le Backend FastAPI et le Dashboard Streamlit dans des conteneurs isolés.

```bash
# Depuis le dossier /project
docker compose up -d
```

### 📍 Accès aux services :
- **API Backend FastAPI** : [http://localhost:8000](http://localhost:8000)
- **Documentation Swagger (API interactive)** : [http://localhost:8000/docs](http://localhost:8000/docs)
- **Dashboard Admin Streamlit** : [http://localhost:8501](http://localhost:8501)
- **Base de données PostgreSQL** : `localhost:5432` (User: `analytics`, DB: `open_analytics`)

### 🛑 Arrêter les conteneurs :
```bash
docker compose down
```

---

## 🛠️ Méthode 2 : Démarrage Manuel en Local (Sans Docker)

Si vous exécutez le projet directement sur votre machine (Windows / Linux / Mac) :

### 1️⃣ Fichier de configuration `.env`
À la racine du projet ou dans `backend/`, assurez-vous d'avoir le fichier `.env` :
```bash
cp .env.example .env
```

---

### 2️⃣ Lancement du Backend (FastAPI)

#### 💻 **Sous Windows (PowerShell / CMD) :**
```powershell
# 1. Se placer dans le dossier backend
cd backend

# 2. Créer l'environnement virtuel (première fois uniquement)
python -m venv .venv

# 3. Activer l'environnement virtuel
.\.venv\Scripts\activate

# 4. Installer les dépendances (dev = prod + pytest/httpx)
pip install -r requirements-dev.txt

# 5. Initialiser / migrer la base de données
alembic upgrade head

# 6. (Optionnel) Générer des données de démonstration
python -m scripts.generate_demo_data

# 7. Démarrer le serveur API Backend
uvicorn app.main:app --reload --port 8000
```

#### 🐧 / 🍎 **Sous Linux / macOS :**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
alembic upgrade head
python -m scripts.generate_demo_data
uvicorn app.main:app --reload --port 8000
```

---

### 3️⃣ Lancement du Dashboard / Frontend (Streamlit)

Ouvrez un **deuxième terminal** (pendant que le backend tourne) :

#### 💻 **Sous Windows (PowerShell / CMD) :**
```powershell
# 1. Se placer dans le dossier dashboard
cd dashboard

# 2. Lancer l'application Streamlit avec le Python de l'environnement virtuel
..\backend\.venv\Scripts\python.exe -m streamlit run app.py
```
*(Si votre terminal a déjà l'environnement virtuel activé, tapez simplement : `streamlit run app.py`)*

#### 🐧 / 🍎 **Sous Linux / macOS :**
```bash
cd dashboard
../backend/.venv/bin/streamlit run app.py
```

---

## 🧪 Exécution des Tests Automatisés (Pytest)

```powershell
# Depuis le dossier backend
cd backend
.\.venv\Scripts\pytest -v
```

---

## 🔑 Variables d'Environnement importantes (`.env`)

| Variable | Valeur par défaut | Description |
|---|---|---|
| `APP_ENV` | `development` | Environnement (`development` / `production`) |
| `DATABASE_URL` | `sqlite:///./analytics.db` | URL DB (`SQLite` en dev local, `PostgreSQL` en prod/docker) |
| `AI_PROVIDER` | `gemini` | Moteur d'analyse IA (`gemini`, `mock`, `local_llm`) |
| `GEMINI_API_KEY` | `AQ...` | Clé d'API Google Gemini AI Studio |
| `API_KEY_HASH_SECRET` | `dev-secret-...` | Clé secrète pour le hachage des clés d'accès applicatives |
| `DASHBOARD_PORT` | `8501` | Port du Dashboard Admin Streamlit |
