# Open Analytics AI — TypeScript / JavaScript SDK (npm)

SDK ultra-léger (0 dépendance externe, compatible Node.js 18+, Bun, Deno, Next.js, Express) pour envoyer vos données au moteur d'analyse décisionnelle et d'explication causale en **une seule ligne de code**.

## Installation

```bash
npm install open-analytics-ai
# ou
pnpm add open-analytics-ai
# ou
yarn add open-analytics-ai
```

## Utilisation Rapide (En 1 Ligne)

```typescript
import { AnalyticsClient } from 'open-analytics-ai';

const client = new AnalyticsClient({ baseUrl: 'http://localhost:8000' });

// 1. Analyse instantanée de données
const result = await client.quickAnalyze({
  data: [
    { date: '2026-10-01', ventes: 150, visiteurs: 3200, panier_moyen: 45.2 },
    { date: '2026-10-02', ventes: 180, visiteurs: 3500, panier_moyen: 48.0 },
    { date: '2026-10-03', ventes: 130, visiteurs: 2900, panier_moyen: 44.5 },
  ],
});

// Résultats décisionnels sans jargon :
console.log(result.insights);
console.log(result.results.causality); // Facteurs d'explication
```

## Comparatif Temporel Automatique (Mois M vs M-1)

Comparez deux périodes temporelles sans jamais devoir fusionner vos fichiers :

```typescript
const comparison = await client.compare({
  periodA: [{ ca: 10000, ventes: 100 }, { ca: 11000, ventes: 110 }],
  periodB: [{ ca: 15000, ventes: 140 }, { ca: 16000, ventes: 150 }],
  periodALabel: 'Mois M-1',
  periodBLabel: 'Mois M',
});

// Sort automatiquement les 3 piliers :
console.log("Ce qui s'est amélioré :", comparison.improved);
console.log("Ce qui s'est dégradé :", comparison.degraded);
console.log("Points de vigilance :", comparison.vigilance_points);
```

## Analyse Formelle avec API Key

```typescript
const client = new AnalyticsClient({
  apiKey: 'anal_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
  baseUrl: 'http://localhost:8000',
});

const report = await client.analyze({
  application: 'farmtinz',
  dataset: 'harvest-sales',
  data: [{ date: '2026-10-01', culture: 'Maïs', quantite_kg: 4500, prix_unitaire: 0.25, revenu_total: 1125 }],
});
```
