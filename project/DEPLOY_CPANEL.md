# Guide de Déploiement du Backend sur cPanel (Phusion Passenger)

Ce guide détaille la mise en production du backend **FastAPI** sur un hébergement cPanel standard via **Setup Python App** (CloudLinux / Phusion Passenger).

---

## 📋 Prérequis & Architecture
* **Hébergeur** : cPanel avec la fonctionnalité **Setup Python App**
* **Version Python supportée** : Python 3.10, 3.11 ou 3.12 (recommandé : **3.11**)
* **Pont WSGI/ASGI** : `a2wsgi` (déjà inclus dans `requirements.txt`)
* **Fichier de démarrage** : `passenger_wsgi.py` (déjà créé à la racine de `backend/`)
* **Recommandation domaine** : Utiliser un sous-domaine dédié comme `api.votredomaine.com` (évite les conflits d'URL avec un WordPress ou site principal).

---

## 🚀 Les 5 Étapes du Déploiement

### Étape 1 : Créer le sous-domaine
1. Dans cPanel, rendez-vous dans la section **Domaines** (ou *Sous-domaines*).
2. Créez un sous-domaine dédié à l'API, par exemple : `api.votredomaine.com`.
3. Notez le répertoire racine associé (ex: `/home/nomuser/api.votredomaine.com`).

---

### Étape 2 : Configurer l'Application Python dans cPanel
1. Rendez-vous dans **Setup Python App** (section *Logiciel* / *Software*).
2. Cliquez sur **Create Application** :
   * **Python version** : Choisissez **3.11** (ou 3.10 / 3.12).
   * **Application root** : Indiquez le chemin du dossier (ex: `api.votredomaine.com` ou `analytics_backend`).
   * **Application URL** : Sélectionnez votre sous-domaine `api.votredomaine.com`.
   * **Application startup file** : `passenger_wsgi.py`
   * **Application Entry point** : `application`
3. Cliquez sur **CREATE** en haut à droite.
4. cPanel crée l'application et génère un environnement virtuel Python avec une ligne de commande d'activation (ex: `source /home/nomuser/virtualenv/.../bin/activate`).

---

### Étape 3 : Téléverser les fichiers du Backend

#### 1. Fichiers à inclure :
* Le dossier `app/` (tout le code source)
* `requirements.txt`
* `passenger_wsgi.py`
* `wsgi.py`
* Le fichier `.env` de production

#### 2. Fichiers à exclure (ne pas téléverser) :
* `.venv/` (l'environnement virtuel est géré par cPanel)
* `__pycache__/` et `.pytest_cache/`
* `analytics.db` locale de test

#### 3. Procédure :
1. Créez une archive ZIP contenant les fichiers du dossier `backend/` (sans `.venv`).
2. Dans cPanel, ouvrez le **Gestionnaire de fichiers** (*File Manager*).
3. Allez dans le dossier racine de votre application (`Application root`).
4. Téléversez le fichier ZIP et cliquez sur **Extraire** (*Extract*).

---

### Étape 4 : Configurer les Variables d'Environnement (.env)
Dans le dossier du backend sur le serveur, créez ou modifiez le fichier `.env` avec vos valeurs de production :

```env
# Environnement
APP_ENV=production
DEBUG=false

# Clé secrète pour les hash de tokens et clés API (chaîne aléatoire complexe)
API_KEY_HASH_SECRET=votre_cle_secrete_longue_et_aleatoire_a_changer

# Fournisseur IA : groq (recommandé) ou mock
AI_PROVIDER=groq
GROQ_API_KEY=votre_cle_groq_gsk_...

# Compte administrateur initial du Dashboard
DASHBOARD_ADMIN_USERNAME=admin
DASHBOARD_ADMIN_PASSWORD=choisissez_un_mot_de_passe_robuste

# Origines autorisées (CORS) : votre domaine frontend ou "*"
CORS_ORIGINS=["*"]
```

---

### Étape 5 : Installer les Dépendances & Démarrer

1. Retournez dans cPanel > **Setup Python App**.
2. Cliquez sur l'icône de modification de votre application.
3. Dans la section **Configuration files**, saisissez `requirements.txt`, cliquez sur **Add**, puis sur **Run Pip Install**.
   * *Alternative via Terminal cPanel* :
     ```bash
     source /home/nomuser/virtualenv/api.votredomaine.com/3.11/bin/activate
     cd /home/nomuser/api.votredomaine.com
     pip install -r requirements.txt
     ```
4. Cliquez sur le bouton **RESTART** pour redémarrer l'application.

---

## 🔍 Vérification & Tests

Une fois redémarrée, l'API est immédiatement accessible en ligne :
* **Documentation Swagger interactive** : `https://api.votredomaine.com/docs`
* **Vérification de santé (Health Check)** : `https://api.votredomaine.com/api/v1/health` (doit renvoyer `{"status": "ok"}`)
source $(find ~/virtualenv -name activate | head -n 1) && cd ~/api.ainalytics.com && pip install --no-cache-dir -r requirements.txt