# 🚀 Guide Déploiement Railway & Kit d'Intégration Collègues

Ce document récapitule les étapes pour déployer le Backend **Open Analytics AI** sur **Railway**, ainsi que la fiche pratique à fournir à vos collègues développeurs pour qu'ils branchent leurs applications.

---

## 🛠️ Partie 1 : Déployer le Backend sur Railway

### 1. Préparation du projet sur Railway
1. Connectez-vous sur [Railway.app](https://railway.app).
2. Cliquez sur **New Project** > **Deploy from GitHub repo**.
3. Sélectionnez le dépôt `analytics`.
4. Dans les paramètres du service (**Settings**) :
   - **Root Directory** : Définissez `backend` (ou laissez la racine si vous utilisez le Procfile/Dockerfile du backend).
   - **Build Command** : Railway détectera automatiquement le `Dockerfile` dans `backend`.

### 2. Variables d'Environnement à configurer sur Railway
Dans l'onglet **Variables** de Railway, ajoutez :

| Variable | Valeur recommandée | Rôle |
|---|---|---|
| `APP_ENV` | `production` | Mode de production |
| `DATABASE_URL` | *(Généré par Railway PostgreSQL)* | URL de connexion DB |
| `AI_PROVIDER` | `gemini` | Fournisseur IA (`gemini` ou `mock`) |
| `GEMINI_API_KEY` | *(Votre clé Google AI Studio)* | Clé d'API pour Gemini |
| `API_KEY_HASH_SECRET` | `votre-cle-secrete-tres-longue-et-securisee` | Hachage sécurisé des clés API |
| `CORS_ORIGINS` | `["*"]` | Autoriser les requêtes web cross-origin |

> 💡 **Conseil Database** : Sur Railway, ajoutez une base de données **PostgreSQL** (New > Database > Add PostgreSQL). Railway créera automatiquement la variable `DATABASE_URL`.

---

## 📦 Partie 2 : Le Kit à fournir à vos Collègues Développeurs

Copiez-collez ce bloc et envoyez-le à vos collègues (sur Slack, Teams, Email, ou Notion) :

---

### 📩 [MESSAGE À COPIER ET ENVOYER AUX COLLÈGUES]

> **Objet :** API Open Analytics AI — URL de test, documentation et instructions de branchement

Hello l'équipe 👋,

Le serveur d'Analytics & IA centralisé **Open Analytics AI** est désormais en ligne sur Railway. Vous pouvez dès maintenant l'intégrer dans vos applications (*Farmtinz, CRMtinz, Sharetinz, etc.*).

#### 📍 1. Liens Utiles
- **URL de Base API** : `https://<VOTRE-APP-RAILWAY>.up.railway.app`
- **Documentation Swagger (Interactive)** : `https://<VOTRE-APP-RAILWAY>.up.railway.app/docs`
- **Health Check** : `https://<VOTRE-APP-RAILWAY>.up.railway.app/api/v1/health`

#### 🔑 2. Authentification & Clé API
Chaque requête d'analyse doit inclure le Header HTTP suivant :
`X-API-Key: anal_<votre_cle_api>`

*(Demandez-moi votre clé API personnalisée ou créez-en une via l'endpoint `/api/v1/applications`)*.

---

#### 🔌 3. Comment brancher votre code ?

Vous devez soumettre vos données au format JSON à l'endpoint `POST /api/v1/analyze`.

##### 🟡 Exemple 1 : JavaScript (Fetch - React / Next.js / Vue / Node)
```javascript
const response = await fetch("https://<VOTRE-APP-RAILWAY>.up.railway.app/api/v1/analyze", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "X-API-Key": "anal_votre_cle_api_ici"
  },
  body: JSON.stringify({
    application_slug: "farmtinz",
    dataset_slug: "harvest-sales",
    analysis: ["summary", "trend", "anomaly"],
    data: [
      { date: "2026-09-01", culture: "Maïs", quantite_kg: 1200, prix_unitaire: 2.5, revenu_total: 3000 },
      { date: "2026-09-08", culture: "Maïs", quantite_kg: 1350, prix_unitaire: 2.5, revenu_total: 3375 },
      { date: "2026-09-15", culture: "Maïs", quantite_kg: 900,  prix_unitaire: 2.4, revenu_total: 2160 },
      { date: "2026-09-22", culture: "Maïs", quantite_kg: 2100, prix_unitaire: 2.6, revenu_total: 5460 }
    ]
  })
});

const result = await response.json();
console.log("Résumé :", result.data.results.summary);
console.log("Tendance :", result.data.results.trend);
console.log("Anomalies :", result.data.results.anomaly);
console.log("Analyse IA :", result.data.ai_interpretation);
```

##### 🐍 Exemple 2 : Python (Requests / Backend-to-Backend)
```python
import requests

url = "https://<VOTRE-APP-RAILWAY>.up.railway.app/api/v1/analyze"
headers = {
    "Content-Type": "application/json",
    "X-API-Key": "anal_votre_cle_api_ici"
}
payload = {
    "application_slug": "crmtinz",
    "dataset_slug": "sales-leads",
    "analysis": ["summary", "trend", "anomaly"],
    "data": [
        {"date": "2026-09-01", "nouveaux_prospects": 45, "conversion_rate": 0.12},
        {"date": "2026-09-08", "nouveaux_prospects": 52, "conversion_rate": 0.15},
        {"date": "2026-09-15", "nouveaux_prospects": 49, "conversion_rate": 0.14}
    ]
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
```

---

## ❓ Partie 3 : Reponses aux questions fréquentes des collègues (FAQ)

### Q1 : *"Où est-ce qu'on branche ce code ?"*
> **Réponse** :
> - **Idéal (Backend-to-Backend)** : Dans le backend de votre application (Node.js/Express, Python, Laravel, etc.) avant de renvoyer le résultat au frontend. Cela évite d'exposer la clé API dans le navigateur du client.
> - **Frontend Direct (React/Vue/Mobile)** : Si vous appelez directement le backend depuis React ou Mobile, stockez la clé API dans les variables d'environnement secrètes du frontend (ex: `.env.local`).

### Q2 : *"J'obtiens une erreur 401 Unauthorized"*
> **Réponse** : Vérifiez que vous avez bien inclus le header HTTP `X-API-Key: anal_...` avec une clé valide associée à votre `application_slug`.

### Q3 : *"J'obtiens une erreur 422 Unprocessable Entity"*
> **Réponse** : Le JSON envoyé ne respecte pas le schéma attendu :
> - La liste `data` ne doit pas être vide.
> - Les noms de champs doivent correspondre aux champs déclarés dans votre dataset.
> - La liste `analysis` doit contenir au moins un des choix : `"summary"`, `"trend"`, `"anomaly"`.

### Q4 : *"Est-ce que nos données confidentielles sont envoyées à OpenAI ou Gemini ?"*
> **Réponse** : **Non !** Le système utilise une architecture Privacy-First. Le backend calcule d'abord les agrégats statistiques anonymes (moyennes, nombres d'anomalies, pourcentages), et c'est **uniquement cet agrégat anonyme** (`AnalyticalContext`) qui est envoyé au modèle d'IA pour obtenir le paragraphe d'analyse.
