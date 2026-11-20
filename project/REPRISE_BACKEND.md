# 📌 POINT D'ARRÊT & GUIDE DE REPRISE — BACKEND CPANEL

**Date de sauvegarde** : 20 Novembre 2026  
**Serveur cPanel** : `s1097`  
**Utilisateur cPanel** : `jolasun`  
**Application / Sous-domaine** : `api.j-ola-sun.com` (Python 3.11)  
**Dossier sur le serveur** : `~/api.ainalytics.com/` (ou `~/api.j-ola-sun.com/`)

---

## 1. Ce qui est déjà fait et validé ✅

1. **Sous-domaine créé** : `api.ainalytics.com`
2. **Application Python configurée dans cPanel** :
   - Version Python : 3.11
   - Startup file : `passenger_wsgi.py`
   - Entry point : `application`
3. **Fichiers backend uploadés et extraits** :
   - `app/`, `scripts/`, `alembic/`, `passenger_wsgi.py`, `wsgi.py`
4. **Fichier `.env` configuré sur le serveur** avec :
   - `APP_ENV=production`
   - `API_KEY_HASH_SECRET=f3a8d91c7b0e25684a1f6c93e4b2d019e85c3b7a6d2e1f4098b7c6d5e4f3a21b`
   - `GROQ_API_KEY=gsk_...`
   - `DASHBOARD_ADMIN_PASSWORD=Masteradmin@9nalytics`
5. **`requirements.txt` adapté pour Python 3.11** (versions flexibles sans le blocage numpy 2.5).

---

## 2. Point de blocage actuel 🛑

- **Erreur** : `[Errno 122] Disk quota exceeded`
- **Cause** : Le quota disque cPanel alloué au compte était insuffisant pour installer `scipy` (il faut ~1 Go à 2 Go de quota disque).
- **En attente** : Augmentation du quota disque par l'hébergeur.

---

## 3. Commandes exactes pour reprendre (dès que le quota est augmenté) 🚀

Ouvrir le **Terminal cPanel** et exécuter cette commande unique :

```bash
source $(find ~/virtualenv -name activate | head -n 1) && cd ~/api.ainalytics.com && pip install --no-cache-dir -r requirements.txt
```

---

## 4. Finalisation après l'installation des dépendances

### A. Redémarrer l'application Python
```bash
touch ~/api.ainalytics.com/tmp/restart.txt
```
*(ou cliquer sur **RESTART** dans l'écran cPanel "Setup Python App")*

### B. Tester que l'API répond
```bash
curl -I http://api.ainalytics.com/api/v1/health
```
*(Résultat attendu : `HTTP/1.1 200 OK` avec `{"status":"ok"}`)*

### C. Seeder les données démo dans l'API en ligne
Depuis ta machine locale (ou depuis le terminal cPanel) :
```bash
python backend/scripts/seed_demo.py http://api.ainalytics.com
```
*(Crée automatiquement les 8 entreprises, 16 jeux de données et le compte admin)*
