# 🌐 GUIDE DÉPLOIEMENT DU FRONTEND SUR CPANEL

Le frontend React est une application statique compilée (HTML, JS, CSS).  
Il ne pèse que **~2 à 3 Mo** et ne consomme aucun quota serveur Python !

---

## Étape 1 : Compiler le frontend en local

Dans ton terminal local sur ta machine :

```bash
cd c:\Users\fayom\Downloads\analytics\project\frontend
npm run build
```

Cela génère un dossier prêt pour la production :
`c:\Users\fayom\Downloads\analytics\project\frontend\dist\`

---

## Étape 2 : Où l'uploader sur cPanel ?

Deux choix selon ton organisation :

- **Option A (Domaine principal)** : Si tu veux le frontend sur `https://ainalytics.com`, ouvre le dossier `public_html/` dans le File Manager de cPanel.
- **Option B (Sous-domaine dédié)** : Si tu veux le frontend sur `https://app.ainalytics.com` (ou `dashboard.ainalytics.com`), crée le sous-domaine dans cPanel puis ouvre son dossier.

---

## Étape 3 : Uploader les fichiers

1. Compresse le **contenu** du dossier `dist/` en ZIP (ou upload directement ses fichiers).
2. Dépose-le dans le dossier cible (`public_html/` ou dossier du sous-domaine).
3. Extrais le ZIP.

Tu dois avoir à la racine du dossier :
```
├── index.html
├── .htaccess
├── assets/
│   ├── index-xxxx.js
│   └── index-xxxx.css
└── demo-samples.json
```

---

## Étape 4 : Tester

Ouvre simplement l'URL dans ton navigateur (ex: `https://ainalytics.com`).  
Le dashboard s'affiche immédiatement !  
Dès que le backend sera relancé, les requêtes partiront vers `https://api.ainalytics.com`.
