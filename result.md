Listed directory project
Listed directory dashboard
Listed directory pages
Viewed analytics.py:1-305
Viewed app.py:1-158
Viewed dataset_definitions.md:1-69

Voici le **plan détaillé d'implémentation et de refonte BI (Business Intelligence)** pour l'interface de restitution d'**Open Analytics AI**. 

Ce plan s'appuie sur une analyse approfondie du backend FastAPI (qui fournit des calculs OLS, IQR, MAD, Pearson, Skewness, Shapiro-Wilk et Forecast), des structures de données (Sales, Farmtinz, CRM) et de l'interface Streamlit existante dans `dashboard/pages/analytics.py`.

---

# 📐 Plan de Refonte BI — Restitution Analytics & Insights

## 1. Diagnostic de l'existant & Vision Cible

| Élément | Interface Actuelle | Nouvelle Interface BI (Cible) |
| :--- | :--- | :--- |
| **Aesthétique** | Basique, emojis informels (`🤖`, `🔴`), containers génériques | Style **Power BI / Tableau** : palette épurée (Slate/Navy/Emerald), typographie professionnelle, cartes KPI avec badges delta, icônes SVG/Lucide. |
| **Graphiques** | Absents ou tableaux bruts | **Graphiques Plotly interactifs** (Courbes temporelles avec bande de confiance, Histogrammes de dispersion, Donut charts, Scatter plots avec droite OLS). |
| **Analyse Statistique** | Masquée ou résumée en texte brut | Section **Constats Mesurables** détaillant pente OLS, $R^2$, $p$-value, corrélations de Pearson $r$ et distribution. |
| **Anomalies** | Simple avertissement avec tableau brut | Matrice de **Vigilance & Anomalies** indiquant la valeur observée, la référence (médiane/moyenne), l'écart relatif, les algorithmes (IQR, MAD, Isolation Forest) et la sévérité. |
| **Insights IA** | Titre principal envahissant avec texte brut | Section secondaire **Insights & Interprétation** découpée en 4 volets : *Observation*, *Interprétation*, *Impact potentiel*, *Limites*. |
| **Recommandations** | Liste de puces informelle | Tableau décisionnel avec *Constat source*, *Action*, *Objectif*, *Priorité*, *KPI cible* et *Échéance*. |
| **Fiabilité & Audit** | Pas de score d'audit visuel | Audit de **Qualité du Dataset** (Complétude, conformité au schéma, valeurs nulles/manquantes, doublons). |

---

## 2. Découpage & Architecture de la Nouvelle Page de Restitution

Le rapport sera réorganisé selon les **9 sections A à I** demandées :

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ A. EN-TÊTE DU RAPPORT — Métadonnées, Filtres & Actions d'Export (PDF / CSV)  │
├─────────────────────────────────────────────────────────────────────────────┤
│ B. SYNTHÈSE EXÉCUTIVE — Cartes KPI (Valeur Clé, Moyenne, Delta %, Volumétrie)│
├─────────────────────────────────────────────────────────────────────────────┤
│ C. VISUALISATION GRAPHIQUE CENTRAL (Plotly)                                │
│    [Évolution Temporelle] [Répartition par Catégorie] [Corrélation / Scatter]│
├─────────────────────────────────────────────────────────────────────────────┤
│ D. ANALYSE STATISTIQUE & MÉTIER — Constats chiffrés (Tendances, OLS, $R^2$)   │
├─────────────────────────────────────────────────────────────────────────────┤
│ E. ANOMALIES & POINTS DE VIGILANCE — Matrice des Écarts & Scores de Consensus│
├─────────────────────────────────────────────────────────────────────────────┤
│ F. INSIGHTS & INTERPRÉTATION IA — Observation / Interprétation / Impact     │
├─────────────────────────────────────────────────────────────────────────────┤
│ G. RECOMMANDATIONS STRATÉGIQUES — Actions, Priorités, KPI & Échéances       │
├─────────────────────────────────────────────────────────────────────────────┤
│ H. QUALITÉ & FIABILITÉ DES DONNÉES — Audit de complétude & intégrité        │
├─────────────────────────────────────────────────────────────────────────────┤
│ I. EXPLORATION INTERACTIVE — Table de données triable & filtrable           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### Detail des Sections & Composants

#### **A. En-tête du Rapport (Report Header)**
- **Intitulé BI** : Titre dynamique basé sur le dataset (ex: *Rapport d'Analyse Exécutive — Demo Sales / Farmtinz Harvest*).
- **Barre d'information** : Badge de l'application cliente, horodatage UTC/Local, nombre total d'enregistrements ($N$), et plage temporelle détectée ($T_{min} \rightarrow T_{max}$).
- **Action Bar** : Boutons d'exportation de données brutes/résultats (CSV / Excel) et bouton d'impression/export PDF du rapport.

#### **B. Synthèse Exécutive (Executive KPI Cards)**
- **Détection automatique du KPI Principal** (ex: `revenue`, `yield_kg`, `deal_value`).
- **Cartes KPI dynamiques avec badges de variation** :
  - *Indicateur Principal (Total / Somme)*
  - *Moyenne & Médiane* (comparaison de centralité)
  - *Taux d'évolution relatif (%)* (calculé via la pente OLS uniquement si une série temporelle est présente)
  - *Volume d'échantillon ($N$ valides)*
  - *Étendue / Min-Max*
- Chaque carte KPI affichera la valeur, l'unité et le delta par rapport au niveau de référence.

#### **C. Visualisation Graphique (Plotly Interactive Charts)**
Sélection dynamique des graphiques Plotly selon le type de colonnes :
1. **Courbe de Tendance & Prévision** (si champ `date` et champ numérique) :
   - Graphique temporel avec courbe OLS et zone d'intervalle de confiance pour les prévisions (`forecast`).
2. **Histogramme / Diagramme de Répartition** (si champ catégoriel `string`) :
   - Diagramme en anneau ou barres horizontales triées par contribution.
3. **Nuage de Points de Corrélation** (si paires numériques avec $r \ge 0.4$) :
   - Scatter plot $X$ vs $Y$ avec ligne de tendance linéaire et valeur du coefficient $r$.
4. **Histogramme de Dispersion & Centiles** (si analyse de distribution) :
   - Box plot ou histogramme montrant $p_{10}, p_{25}, p_{50}, p_{75}, p_{90}$.

#### **D. Analyse Statistique & Métier**
- Formutation sous forme de **Constats Mesurables** issus des calculs backend :
  - **Tendances OLS** : *« Tendance à la hausse détectée sur `revenue` (+12.4% par période, $R^2 = 0.88, p < 0.001$). »*
  - **Corrélations** : *« Corrélation positive forte entre `surface_ha` et `yield_kg` ($r = 0.91$). Attention : corrélation statistique n'implique pas de causalité directe. »*
  - **Asymétrie de Distribution** : *« Distribution asymétrique à droite sur `cost` (skewness = +1.45). »*

#### **E. Anomalies & Points de Vigilance**
- Tableau interactif et cartes d'alerte pour les anomalies détectées par le backend :
  - **Colonne & Ligne** concernée.
  - **Valeur observée** vs **Valeur moyenne/médiane de référence**.
  - **Écart mesuré** (Score Z / MAD / Déviation IQR).
  - **Méthodes d'accord** (IQR, MAD, Isolation Forest) avec score de confiance du consensus ($\ge 66\%$).

#### **F. Insights & Interprétation par l'IA**
- Présentation en section secondaire (pour éviter la domination de l'IA) :
  - **Observation** : Constat factuel directement vérifiable dans les données.
  - **Interprétation** : Hypothèse ou signification métier.
  - **Impact potentiel** : Conquéquences pour l'activité.
  - **Limites** : Informations manquantes ou biais potentiels.
- Badge d'indication de la confiance de l'IA (distingué des métriques de significativité statistique).

#### **G. Recommandations Stratégiques**
- Tableau d'action opérationnel :
  - *Constat d'origine* $\rightarrow$ *Action proposée* $\rightarrow$ *Objectif* $\rightarrow$ *Priorité (Haute/Moyenne/Basse)* $\rightarrow$ *KPI de suivi*.
  - Aucune promesse de ROI chiffré sans données d'investissement réelles.

#### **H. Qualité & Fiabilité des Données (Data Quality Audit)**
- Indicateurs d'audit du dataset :
  - Nombre de lignes reçues vs lignes valides ($100\%$ conformité).
  - Taux de complétude par colonne (détection des `null`/`NaN`).
  - Doublons d'enregistrements.
  - Indicateur visuel d'adéquation du volume d'échantillon ($N \ge 30$).

#### **I. Exploration des Données (Data Table)**
- Tableau Streamlit interactif (`st.dataframe`) avec tri par colonne, recherche textuelle et téléchargement direct au format CSV/Excel.

---

## 3. Charte Graphique & Design System BI

- **Palette de couleurs** :
  - Header & Structure : Navy / Slate (`#1E293B`, `#0F172A`)
  - Accent / Tendance Positives : Emerald (`#10B981`)
  - Alertes / Anomalies : Crimson (`#EF4444`)
  - Avertissements / Risques : Amber (`#F59E0B`)
  - Visualisations / Data : Blue Indigo (`#3B82F6`, `#6366F1`)
- **CSS personnalisé** : Injection CSS propre via `st.markdown` pour obtenir des cartes KPI ombragées avec bordures fines (`1px solid #E2E8F0`), éliminant l'apparence Streamlit brute.

---

## 4. Garanties de Rigueur & Non-Falsification des Données

1. **Zéro Donnée Fictive** : Tous les graphiques et KPI exploiteront exclusivement le JSON de résultat renvoyé par `/api/v1/analyze` ou le DataFrame d'entrée.
2. **Distinction Confiance IA vs Significativité Statistique** : Le score $R^2$ et la $p$-value seront affichés pour la statistique, tandis que le score de l'IA sera cantonné à son bloc dédié.
3. **Absence de Tendance Forcée** : Si $R^2 < 0.25$ ou $p \ge 0.05$, la tendance sera marquée comme *"Non significative (bruit naturel)"*.

---

## 5. Déroulement de l'Implémentation

1. **Création d'un module UI dédié (`dashboard/components/bi_report.py`)** contenant les fonctions de rendu modulaire par section (A à I) et le thème Plotly.
2. **Intégration et mise à jour de la page `dashboard/pages/analytics.py`** pour brancher le nouveau rendu BI à l'exécution des analyses.
3. **Validation & Vérification de Rendu** sur les 3 types de datasets de démonstration (Ventes e-commerce, Récoltes agricoles Farmtinz, Pipeline CRM).

---

> ❓ **Validation :** Souhaitez-vous que je procède immédiatement à l'implémentation de cette refonte UI dans le code ?