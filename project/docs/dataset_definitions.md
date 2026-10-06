# Exemples de Définitions de Champs pour Créer vos Datasets dans l'Interface

Collez directement ces blocs JSON dans le champ **"Définition des champs (tableau JSON — au moins 1 champ requis)"** de votre dashboard.

---

## 1. Dataset Ventes & E-Commerce (`demo-sales`)

* **Nom du Dataset :** `Demo Sales`
* **Slug du Dataset :** `demo-sales`
* **Description :** `Données de ventes e-commerce pour analyse de chiffre d'affaires et détection d'anomalies`

### JSON à copier / coller :
```json
[
  {"name": "date", "technical_type": "date", "semantic_type": "date", "required": true},
  {"name": "product", "technical_type": "string", "semantic_type": "product", "required": true},
  {"name": "category", "technical_type": "string", "semantic_type": "category", "required": false},
  {"name": "quantity", "technical_type": "integer", "semantic_type": "quantity", "unit": "unités", "required": true},
  {"name": "unit_price", "technical_type": "float", "semantic_type": "cost", "unit": "EUR", "required": true},
  {"name": "revenue", "technical_type": "float", "semantic_type": "revenue", "unit": "EUR", "required": true},
  {"name": "cost", "technical_type": "float", "semantic_type": "cost", "unit": "EUR", "required": true},
  {"name": "region", "technical_type": "string", "semantic_type": "location", "required": false}
]
```

---

## 2. Dataset Agricole Farmtinz (`farmtinz-harvest`)

* **Nom du Dataset :** `Farmtinz Harvest`
* **Slug du Dataset :** `farmtinz-harvest`
* **Description :** `Suivi des récoltes, parcelles et météo agricole`

### JSON à copier / coller :
```json
[
  {"name": "date", "technical_type": "date", "semantic_type": "date", "required": true},
  {"name": "parcel_id", "technical_type": "string", "semantic_type": "identifier", "required": true},
  {"name": "crop_type", "technical_type": "string", "semantic_type": "category", "required": true},
  {"name": "surface_ha", "technical_type": "float", "semantic_type": "quantity", "unit": "ha", "required": true},
  {"name": "yield_kg", "technical_type": "float", "semantic_type": "quantity", "unit": "kg", "required": true},
  {"name": "temperature_c", "technical_type": "float", "semantic_type": "metric", "unit": "°C", "required": false},
  {"name": "rainfall_mm", "technical_type": "float", "semantic_type": "metric", "unit": "mm", "required": false},
  {"name": "humidity_pct", "technical_type": "integer", "semantic_type": "metric", "unit": "%", "required": false}
]
```

---

## 3. Dataset CRM & Funnel de Vente (`crmtinz-pipeline`)

* **Nom du Dataset :** `CRMTinz Pipeline`
* **Slug du Dataset :** `crmtinz-pipeline`
* **Description :** `Pipeline commercial, opportunités et conversion de leads`

### JSON à copier / coller :
```json
[
  {"name": "date", "technical_type": "date", "semantic_type": "date", "required": true},
  {"name": "lead_id", "technical_type": "string", "semantic_type": "identifier", "required": true},
  {"name": "source", "technical_type": "string", "semantic_type": "category", "required": false},
  {"name": "status", "technical_type": "string", "semantic_type": "status", "required": true},
  {"name": "deal_value", "technical_type": "float", "semantic_type": "revenue", "unit": "EUR", "required": true},
  {"name": "response_time_hours", "technical_type": "float", "semantic_type": "metric", "unit": "h", "required": false},
  {"name": "converted", "technical_type": "boolean", "semantic_type": "status", "required": true}
]
```
