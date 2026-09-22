# Architecture

## System Overview

Open Analytics AI is designed as a modular platform with clear separation of concerns.

```
┌─────────────────┐     ┌─────────────────┐
│  React App A    │     │  React App B    │
│  (Farmtinz)     │     │  (CRMtinz)      │
└────────┬────────┘     └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     │ REST API (JSON)
         ┌───────────▼───────────┐
         │    FastAPI Backend     │
         │    /api/v1/*           │
         ├───────────────────────┤
         │  Auth (API Key)       │
         │  Rate Limiting        │
         │  CORS                 │
         ├───────────────────────┤
         │  Application Registry │
         │  Dataset Registry     │
         │  Data Validation      │
         ├───────────────────────┤
         │  Analytics Engine     │
         │  ├── Summary          │
         │  ├── Trend            │
         │  └── Anomaly          │
         ├───────────────────────┤
         │  Insight Engine       │
         ├───────────────────────┤
         │  AI Engine            │
         │  ├── MockAIProvider   │
         │  └── LocalLLMProvider │
         ├───────────────────────┤
         │  PostgreSQL + SQLAlch │
         └───────────────────────┘
                     │
         ┌───────────▼───────────┐
         │  Streamlit Dashboard  │
         │  (Internal Admin)     │
         └───────────────────────┘
```

## Backend Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── api/
│   │   ├── router.py        # Route aggregation
│   │   ├── dependencies.py  # Auth, pagination
│   │   └── routes/          # Endpoint modules
│   │       ├── health.py
│   │       ├── applications.py
│   │       ├── datasets.py
│   │       ├── analytics.py
│   │       └── insights.py
│   ├── core/
│   │   ├── config.py        # Settings from env
│   │   ├── database.py      # SQLAlchemy engine
│   │   ├── security.py      # API key management
│   │   └── logging.py       # Structured logging
│   ├── models/              # SQLAlchemy ORM models
│   ├── schemas/             # Pydantic validation
│   ├── repositories/        # Data access layer
│   └── services/
│       ├── analytics/       # Summary, Trend, Anomaly
│       ├── ai/              # AI provider abstraction
│       └── insights/        # Insight generation
├── tests/                   # Unit tests
├── scripts/                 # Utility scripts
├── alembic/                 # Database migrations
└── requirements.txt
```

## Key Design Decisions

### 1. Privacy-First AI

The AI engine never receives raw data. Instead, an `AnalyticalContext` object is built containing only:
- Statistical summaries
- Trend indicators
- Anomaly counts
- Generated insights

This ensures sensitive data is never exposed to LLM providers.

### 2. Pluggable Analytics

Each analytics service inherits from `BaseAnalyticsService` and is registered with the `AnalyticsEngine`. Adding new analysis types requires:
1. Creating a new service class
2. Registering it in the engine

### 3. Application Isolation

Each registered application gets:
- A unique API key (hashed in database)
- Isolated datasets
- Independent analysis runs

### 4. Repository Pattern

All database access goes through repositories, keeping business logic clean and testable.

## Database Schema

- **Application**: name, slug, api_key_hash, status
- **Dataset**: application_id, name, slug, description
- **DatasetField**: dataset_id, name, type, semantic_type, unit, required
- **AnalysisRun**: application_id, dataset_id, analysis_types, status, result
- **Insight**: analysis_run_id, type, severity, title, description, metric, value

## Technology Stack

| Component | Technology |
|-----------|-----------|
| API Framework | FastAPI |
| Validation | Pydantic |
| ORM | SQLAlchemy |
| Database | PostgreSQL |
| Migrations | Alembic |
| Analytics | Pandas, NumPy, SciPy |
| ML | Scikit-learn |
| AI | Pluggable (Mock / Ollama) |
| Dashboard | Streamlit |
| Containerization | Docker |
