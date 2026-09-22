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
  }
}
```

#### `GET /api/v1/analysis`

List recent analysis runs.

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
