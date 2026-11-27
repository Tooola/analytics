# OPEN ANALYTICS AI — CAHIER DES CHARGES TECHNIQUE & ROADMAP V2
> **Document de Référence & Vision Stratégique**  
> **Statut :** Spécification préparatoire — Développement V2 soumis à autorisation préalable expresse.  
> **Version cible :** 2.0.0  
> **Auteur :** Open Analytics AI Architecture Team  
> **Date de rédaction :** 23 novembre 2026  

---

## 1. VISION DE LA VERSION 2 (V2)

### 1.1 De l'outil statistique à la plateforme d'intelligence décisionnelle
Open Analytics AI a été conçu initialement comme un moteur centralisé d'analyses statistiques et d'interprétation automatisée par IA. La version 1 (V1) a posé des fondations robustes : validation formelle de schémas, détection d'anomalies par consensus statistique, calculs de tendances et synthèse narrative sans jargon mathématique.

La **Version 2 (V2)** a pour ambition de transformer Open Analytics AI en une **véritable plateforme de Business Intelligence (BI) assistée par Intelligence Artificielle**, utilisable et intelligible à la fois par :
1. **Les dirigeants et directeurs opérationnels** : qui recherchent des réponses directes, des constats hiérarchisés par impact business et des plans d'action concrets, sans barrière technique ni surcharge d'acronymes.
2. **Les analystes de gestion et data managers** : qui ont besoin de traçabilité, de contrôle fin des dimensions, d'exploration granulaire des données sous-jacentes et de comparaisons multidimensionnelles fiables.

### 1.2 Principes directeurs de la V2
- **Zéro boîte noire statistique** : Chaque constat ou recommandation formulé par l'IA doit être corrélé à des faits statistiques mesurés et auditables.
- **Sobriété cognitive** : Élimination du bruit visuel, hiérarchisation stricte de l'information (du niveau exécutif macroscopique jusqu'au détail unitaire).
- **Indépendance stricte des couches** : Séparation totale entre le moteur de calcul mathématique déterministe (Python/Pandas/Scipy) et la couche narrative générative (LLM).

---

## 2. OBJECTIFS FONCTIONNELS DE LA V2

La V2 introduira dix piliers fonctionnels majeurs :

### 2.1 Nouvelle Synthèse Exécutive (Executive Brief)
- Restitution d'un **Scorecard Exécutif** en tête de rapport répondant en 30 secondes à trois questions capitales pour un dirigeant :
  1. *Quelle est la santé globale de l'activité sur la période ?* (Trajectoire : En croissance / Sous tension / Stable / À surveiller).
  2. *Quelles sont les victoires notables et les points de repli majeurs ?*
  3. *Quelle décision prioritaire doit être prise cette semaine ?*
- Élimination des pourcentages fictifs ou non étayés : affichage d'un indicateur de complétude et de solidité de l'échantillon.

### 2.2 Explications Métier des Statistiques
- Fin des termes mathématiques déconnectés du quotidien opérationnel.
- Remplacement systématique de la technicité par le contexte business :
  - *Au lieu de "Asymétrie positive / Distribution asymétrique à droite"* ➔ *"Quelques très fortes valeurs tirent la moyenne vers le haut tandis que la majorité des cas se situent plus bas."*
  - *Au lieu de "R² = 0.89 / Pente positive"* ➔ *"Progression régulière et durable confirmée tout au long de la période."*
  - *Au lieu de "Écart-type élevé"* ➔ *"Forte dispersion : performances hétérogènes d'une observation à l'autre."*

### 2.3 Visualisation Graphique Intelligente & Interactive
- **Auto-sélection du type de graphique** selon la nature des variables :
  - Séries temporelles ➔ Courbes lissées avec zone d'intervalle de confiance.
  - Répartition par catégories ➔ Barres horizontales classées ou treemaps.
  - Corrélations croisées ➔ Matrice d'impact visuelle et nuages de points avec droite de tendance.
- **Interactivité augmentée** : infobulles enrichies, mise en surbrillance instantanée des points atypiques directement sur le tracé, zoom dynamique sur les périodes d'inflexion.

### 2.4 Détection & Qualification Précise des Anomalies
- Catégorisation explicite des signaux détectés :
  - *Anomalies statistiques extrêmes* (pics ou creux historiques non reproductibles).
  - *Ruptures de tendance* (décrochage brutal de trajectoire).
  - *Incohérences de données ou saisies suspectes* (valeurs négatives sur une métrique strictement positive, zéros suspects).
  - *Données manquantes ou incomplètes*.
- **Déduplication stricte** : décompte précis du nombre d'enregistrements touchés pour ne jamais compter trois fois le même incident sur trois colonnes.

### 2.5 Recommandations Décisionnelles Contextualisées
- Production de recommandations hiérarchisées selon deux axes :
  - **Impact potentiel** (Faible / Moyen / Majeur).
  - **Horizon d'action** (Immédiat sous 48h / Court terme sous 30 jours / Stratégique).
- Formulation prescriptive : associer à chaque problème constaté la cause probable et le levier opérationnel actionnable.

### 2.6 Plan d'Action Décisionnel Structuré
- Transformation des recommandations en une feuille de route opérationnelle (To-Do de direction).
- Distinction claire entre les actions correctives urgentes et le suivi de routine.
- Option d'export du plan d'action en format synthétique (PDF exécutif, markdown, presse-papier).

### 2.7 Exploration des Données Brutes (Data Explorer)
- Modernisation du visualiseur de données tabulaires :
  - Pagination côté client et côté serveur pour les jeux volumineux.
  - Recherche plein texte et filtres rapides par colonne.
  - Marquage visuel (badge ambré) sur les cellules précises ayant déclenché un point de vigilance.
  - Export instantané au format CSV / Excel / JSON.

### 2.8 Comparaison Temporelle & Multi-Canaux
- Généralisation du comparatif temporel (Mois M vs M-1, Année N vs N-1, Semaine S vs S-1).
- Intégration de la comparaison multi-canaux (comparaison de deux segments, deux agences, deux typologies de clients ou deux gammes de produits).
- Analyse en Face-à-Face consolidé (*What Improved* vs *What Degraded*).

### 2.9 Simplification Radicale de l'Expérience Utilisateur (UX)
- Réduction de la charge mentale : formulaires adaptatifs masquant automatiquement les réglages avancés lorsqu'ils ne sont pas nécessaires.
- États de chargement informatifs (*Skeleton screens* animés décrivant les étapes du calcul : validation, moteurs statistiques, modélisation IA).
- Mode sombre et mode clair parfaitement contrastés, conformes aux standards d'accessibilité WCAG 2.1 AA.
- Responsive design irréprochable sur smartphone, tablette et écran large 4K.

### 2.10 Internationalisation Intégrale (FR / EN)
- Support bilingue total et sans faille :
  - Interface utilisateur (textes, boutons, infobulles, modales, notifications).
  - Synthèses rédigées par l'IA (génération native dans la langue cible).
  - Explications des anomalies et libellés d'actions.
  - Formatage localisé des nombres et devises (`1 234,50 €` en FR vs `$1,234.50` en EN).

---

## 3. ARCHITECTURE TECHNIQUE ACTUELLE & PROJECTION V2

L'architecture existante mise en lumière lors de l'audit technique est solide, modulaire et découplée.

```
┌────────────────────────────────────────────────────────────────────────┐
│                          FRONTEND REACT 19 (SPA)                       │
│  Vite 8 • Tailwind CSS v4 • Lucide React • Recharts • Context i18n/Thème│
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP / JSON (Fetch Client)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                          FASTAPI BACKEND (Python)                      │
│  Routes REST /api/v1 • SlowAPI Rate Limiter • Pydantic v2 • SQLAlchemy │
└──────────────┬──────────────────────────────────────────┬──────────────┘
               │                                          │
               ▼                                          ▼
┌──────────────────────────────┐        ┌────────────────────────────────┐
│      MOTEUR ANALYTIQUE       │        │         MOTEUR D'IA            │
│  DataValidator               │        │  AIEngine (Sanitisation)       │
│  AnalyticsEngine             │        │  GroqProvider (LLaMA 3.3 70B)  │
│  Summary, Trend, Anomaly     │        │  GeminiProvider                │
│  Correlation, Causality      │        │  LocalLLM (Ollama)             │
│  PeriodComparator            │        │  MockAIProvider (Fallback)     │
│  ConsolidatedSynthesis       │        └────────────────────────────────┘
│  (Pandas, NumPy, Scikit-learn│
│   SciPy, Statsmodels)        │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│     PERSISTANCE & ACCÈS      │
│  PostgreSQL / SQLite         │
│  Applications / Datasets     │
│  Clés API Tenants            │
└──────────────────────────────┘
```

### 3.1 Composants sanctuarisés (À CONSERVER EN V2)
- **FastAPI & Dépendances REST** : Architecture asynchrone légère, routeur modulaire, documentation OpenAPI.
- **Pydantic v2** : Validation stricte des contrats de données aux frontières du système.
- **Moteur d'orchestration statistique (`AnalyticsEngine`)** : Modèle d'enregistrement de services unifiés (`BaseAnalyticsService`).
- **Algorithmes statistiques robustes** : Consensus d'anomalies (IQR + MAD + Isolation Forest), régression linéaire OLS, corrélations de Pearson/Spearman.
- **Isolation multi-tenant sécurisée** : Isolation par clé API d'application (`X-API-Key`).
- **Protocole de sanitarisation IA** : Interdiction absolue de transmettre des données brutes aux LLMs tiers (seuls les agrégats statistiques anonymisés nourrissent le prompt).

### 3.2 Composants appelés à évoluer en V2
- **Système de composants Frontend** : Évolution vers une bibliothèque de composants atomiques plus typée et découplée.
- **Moteur de Graphiques** : Remplacement des graphiques Recharts statiques par un système de visualisations interactives unifiées avec export image HD/SVG.
- **Moteur de métriques de confiance IA** : Abandon des pourcentages statiques/mockés au profit d'un véritable indice d'exploitabilité statistique calculé sur la taille d'échantillon et la dispersion des données.
- **Pagination & Streaming d'analyse** : Pour les jeux de données volumineux (> 10 000 lignes), passage à un traitement par batch avec indicateur de progression temps réel (Server-Sent Events ou WebSockets).

---

## 4. PLAN DE DÉVELOPPEMENT PROGRESSIF DE LA V2

Le développement de la V2 sera découpé en 6 phases étanches. Aucune phase ne débutera sans la validation formelle des critères de la phase précédente.

| Phase | Intitulé | Objectifs majeurs | Dépendances | Risques | Critères de validation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **P1** | **Design System & Socle UI V2** | Tokens visuels, composants KPI unifiés, squelettes de chargement, accessibilité WCAG | Tailwind CSS v4, Lucide | Incohérence de thèmes clair/sombre | 100% des composants de base testés dans Storybook ou banc d'essai |
| **P2** | **Refonte du Moteur de Restitution Exécutive** | Scorecard dirigeant, reformulation littérale des constats, suppression du jargon | P1, Services insights existants | Résistance au changement des utilisateurs data | Test utilisateur concluant sur un panel de 3 profils non-techniciens |
| **P3** | **Module de Visualisation Interactive** | Graphiques Recharts réactifs, mise en évidence des anomalies au clic, filtres temporels | P1, P2 | Lenteur sur grands jeux de données | Rendu fluide (< 16ms / 60fps) sur 1 000 points affichés |
| **P4** | **Explorateur de Données & Alertes Dédupliquées** | Tableau interactif avec tri, recherche, pagination et déduplication des anomalies | P1, P3, API Analytics | Surcharge mémoire navigateur | Tri et filtrage instantané sur tableau de 5 000 lignes |
| **P5** | **Comparateur Multidimensionnel Avancé** | Comparatif temporel étendu (M/M-1, N/N-1) et comparatif multi-canaux/segments | P2, P3, PeriodComparator | Complexité des schémas non homogènes | Comparatif robuste avec colonnes asymétriques |
| **P6** | **Internationalisation & Recette Globale** | Vérification bilingue 100%, tests de non-régression de bout en bout, audit de sécurité | Toutes phases | Clés i18n manquantes | 94 tests backend passants, 0 erreur de lint/build frontend |

---

## 5. COMPATIBILITÉ, SÉCURITÉ & CONTINUITÉ DE SERVICE

### 5.1 Préservation des API existantes & Non-Régression
- Les signatures des routes actuelles (`/api/v1/analyze`, `/api/v1/analyze/quick`, `/api/v1/analyze/quick/compare`, `/api/v1/analyze/multi`) sont **intangibles**.
- Aucune rupture de contrat JSON ne sera introduite. Si de nouvelles propriétés sont ajoutées, elles seront purement optionnelles et rétrocompatibles.
- Les applications tierces déjà connectées (Farmtinz, CRMtinz, Sharetinz) continueront de fonctionner sans modification de leur code.

### 5.2 Sécurité & Confidentialité des Données
- Maintien du principe de **Confidentialité par Conception** (*Privacy by Design*) :
  - Aucune ligne de données nominatives ne doit transiter vers les API des fournisseurs de LLM (Groq, Google Gemini, OpenAI).
  - Les clés API d'application stockées en base restent hachées selon les meilleurs standards de sécurité.
  - Le rate limiting par IP et par clé d'application est maintenu et renforcé.

### 5.3 Stratégie de Retour Arrière (Rollback)
- Chaque étape de déploiement doit être versionnée via Git avec des points d'arrêt identifiés.
- En cas d'anomalie critique sur une phase V2, la bascule vers la V1 doit être possible en moins de 5 minutes par réversion du conteneur/branche de build, sans perte de données.
- Aucune migration de schéma de base de données destructrice (DROP TABLE, DROP COLUMN) n'est autorisée.

---

## 6. CONDITIONS DE DÉMARRAGE DE LA V2

> ### ⚠️ RÈGLE DE GOUVERNANCE STRICTE
> Le développement effectif de la version 2 (V2) est **strictement suspendu** à ce jour.  
> **Aucun code source V2 ne devra être produit, aucune dépendance ajoutée et aucun composant existant altéré** tant que l'autorisation explicite et formelle n'aura pas été donnée par le responsable du projet.  
> 
> La version actuelle (V1) demeure la seule version active, maintenue et opérationnelle en production.
