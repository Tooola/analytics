# API Reference

Base URL: `http://localhost:8000/api/v1`

## Authentication

Most endpoints require an API key via the `X-API-Key` header:

```
X-API-Key: anal_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Endpoints

### Health

#### `GET /api/v1/health`

Check system health.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "ai_provider": "mock",
  "timestamp": "2024-01-15T10:30:00"
}
```

---

### Applications

#### `POST /api/v1/applications`

Register a new application.

**Request:**
```json
{
  "name": "Farmtinz",
  "description": "Livestock management platform",
  "status": "active"
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "Farmtinz",
  "slug": "farmtinz",
  "description": "Livestock management platform",
  "status": "active",
  "api_key": "anal_xxxxx..."
}
```

> Save the `api_key` — it is only shown once.

#### `GET /api/v1/applications`

List all applications.

#### `GET /api/v1/applications/{id}`

Get application by ID.

#### `PUT /api/v1/applications/{id}`

Update an application.

#### `DELETE /api/v1/applications/{id}`

Delete an application.

#### `POST /api/v1/applications/{id}/regenerate-key`

Generate a new API key (old key is invalidated).

#### `POST /api/v1/applications/{id}/revoke-key`

Revoke the application's API key.

---

### Datasets

#### `POST /api/v1/datasets`

Register a dataset with field definitions.

**Headers:** `X-API-Key: YOUR_KEY`

**Request:**
```json
{
  "application_slug": "farmtinz",
  "name": "Livestock",
  "slug": "livestock",
  "description": "Livestock records",
  "fields": [
    {"name": "animal_id", "type": "string", "required": true},
    {"name": "weight", "type": "float", "unit": "kg", "required": true},
    {"name": "birth_date", "type": "date", "required": true},
    {"name": "mortality", "type": "boolean", "required": false}
  ]
}
```

#### `GET /api/v1/datasets`

List datasets. Optional query: `?application_slug=farmtinz`

#### `GET /api/v1/datasets/{id}`

Get dataset with fields.

#### `PUT /api/v1/datasets/{id}`

Update dataset (requires auth + ownership).

#### `DELETE /api/v1/datasets/{id}`

Delete dataset (requires auth + ownership).

---

### Analytics

#### `POST /api/v1/analyze`

Run analysis on data.

**Headers:** `X-API-Key: YOUR_KEY`

**Request:**
```json
{
  "application_slug": "farmtinz",
  "dataset_slug": "livestock",
  "analysis": ["summary", "trend", "anomaly"],
  "include_ai": true,
  "data": [
    {"animal_id": "A001", "weight": 45.2, "birth_date": "2024-01-15", "mortality": false},
    {"animal_id": "A002", "weight": 38.7, "birth_date": "2024-02-20", "mortality": true}
  ]
}
```

**Response:**
```json
{
  "success": true,
  "analysis_id": "uuid",
  "summary": {
    "weight": {"count": 2, "mean": 41.95, "min": 38.7, "max": 45.2, "std": 4.6}
  },
  "trends": {
    "weight": {"direction": "down", "change_percent": -14.4}
  },
  "anomalies": {
    "weight": []
  },
  "insights": [
    {
      "type": "trend",
      "severity": "low",
      "title": "Weight statistics",
      "description": "Average weight: 41.95 across 2 records"
    }
  ],
  "ai_interpretation": {
    "provider": "mock",
    "summary": "Analysis shows...",
    "key_findings": ["..."],
    "recommendations": ["..."],
    "confidence": 0.75
  },
  "ai_status": "ok"
}
```

`ai_status`: `null` = AI not requested, `"ok"` = interpretation delivered,
`"error"` = requested but the provider returned nothing (statistical results
are still delivered). Same field on `/analyze/multi` and `/analyze/quick`.

#### `POST /api/v1/analyze/multi`

Consolidated analysis: **several datasets of one application in ONE pass** —
per-dataset results + links BETWEEN datasets + a decision synthesis.

Each dataset is validated, analysed and persisted under its own run; on top
of that the endpoint aligns the datasets on `join_key`, computes
cross-dataset correlations, and builds a consolidated verdict. Typical use:
a structure with several departments/sources (ventes, achats, électricité…).

**Headers:** `X-API-Key: YOUR_KEY`

**Limits:** max 10 datasets, 10 000 rows per payload, `analyze_multi_per_minute`
per client bucket (default 10/min).

**Request:**
```json
{
  "application": "structure-finance",
  "datasets": ["ventes-terrain", "achats-maison", "electricite"],
  "analysis": ["summary", "trend", "anomaly", "correlation"],
  "join_key": "mois",
  "include_ai": true,
  "payloads": {
    "ventes-terrain": [
      {"mois": "2026-01", "montant": 12000},
      {"mois": "2026-02", "montant": 15500}
    ],
    "achats-maison": [
      {"mois": "2026-01", "montant": 8000},
      {"mois": "2026-02", "montant": 9500}
    ],
    "electricite": [
      {"mois": "2026-01", "montant": 420},
      {"mois": "2026-02", "montant": 460}
    ]
  }
}
```

- `payloads` keys must match `datasets` exactly (422 otherwise).
- `join_key`: common column aligning rows across datasets (`mois`, `date`…).
  Omit it to run per-dataset analysis only — cross links are then skipped
  (never guessed), and the synthesis says so.

**Response:**
```json
{
  "success": true,
  "application": "structure-finance",
  "datasets": ["ventes-terrain", "achats-maison", "electricite"],
  "join_key": "mois",
  "validations": {"ventes-terrain": {"valid": true, "row_count": 2}, "...": {}},
  "results": {"ventes-terrain": {"summary": [], "trend": [], "...": []}, "...": {}},
  "insights": {"ventes-terrain": [{"type": "trend", "title": "..."}], "...": []},
  "cross_correlations": [
    {
      "dataset1": "ventes-terrain", "column1": "montant",
      "dataset2": "achats-maison", "column2": "montant",
      "coefficient": 0.98, "p_value": 0.001,
      "strength": "strong", "relationship": "positive"
    }
  ],
  "synthesis": {
    "datasets_analyzed": 3,
    "total_rows": 6,
    "join_key": "mois",
    "trends": {"ventes-terrain": "up", "electricite": "up"},
    "divergent": false,
    "top_links": ["..."],
    "risks": [],
    "verdict": "positif",
    "summary": "3 jeu(x) de données analysés en une seule passe..."
  },
  "ai_interpretation": "{\"provider\": \"...\", \"summary\": \"...\"}",
  "analysis_ids": {"ventes-terrain": "uuid", "achats-maison": "uuid", "electricite": "uuid"}
}
```

- **One run per dataset** — history (`GET /api/v1/analysis`) stays per-dataset.
- `cross_correlations`: `|r| >= 0.4`, `p < 0.05`, ≥5 aligned rows, strongest
  first (max 20). Constant columns never yield a link.
- `synthesis.verdict`: `positif` | `equilibre` | `tension` | `surveiller`
  (risks beat divergence beat direction).
- `success: false` when any dataset fails validation: that dataset appears in
  `validations` (invalid) with a `failed` run id, the others still report —
  and the consolidated layer (`cross_correlations`, `synthesis`) is withheld.
- `include_ai: true` feeds the whole picture (all datasets + synthesis) to
  the AI provider in one interpretation.

#### `GET /api/v1/analysis`

List recent analysis runs. Query: `?limit=1..200` (default 50) and
`?skip=0` (pagination cursor — skip the N newest rows; empty array = end
of history).

#### `GET /api/v1/analysis/{run_id}`

Get analysis run details with insights.

---

### Insights

#### `GET /api/v1/insights`

List insights. Optional query: `?run_id=uuid&limit=50`

---

### Analysis Types

| Type | Description |
|------|-------------|
| `summary` | Count, mean, median, min, max, std for numeric fields |
| `trend` | Period-over-period change, direction, percentage |
| `anomaly` | Z-score based outlier detection |

---

### Field Types

| Technical Type | Description |
|---------------|-------------|
| `string` | Text data |
| `integer` | Whole numbers |
| `float` | Decimal numbers |
| `boolean` | True/false |
| `date` | Date (YYYY-MM-DD) |
| `datetime` | Date + time |

### Semantic Types

| Semantic Type | Description |
|--------------|-------------|
| `revenue` | Income/sales amounts |
| `cost` | Expenses/costs |
| `quantity` | Counts/amounts |
| `date` | Date references |
| `product` | Product names/IDs |
| `customer` | Customer references |
| `location` | Geographic data |

---

## Error Responses

```json
{
  "success": false,
  "errors": [
    {"field": "weight", "error": "Expected number"},
    {"field": "date", "error": "Invalid date format"}
  ]
}
```

## Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad request / validation error |
| 401 | Missing or invalid API key |
| 404 | Resource not found |
| 500 | Internal server error |
