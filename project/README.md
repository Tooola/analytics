# Open Analytics AI

Analytics and AI interpretation platform for multi-application environments.

## Overview

Open Analytics AI is a reusable backend that provides analytics, trend analysis, anomaly detection, and AI-powered insights to React applications via a REST API.

**Supported client applications**: Farmtinz, CRMtinz, Sharetinz, and any future apps.

## Quick Start

### Using Docker (recommended)

```bash
cp .env.example .env   # fill in POSTGRES_PASSWORD (and GROQ_API_KEY if used)
docker compose up
```

This starts:
- **FastAPI** at http://localhost:8000
- **Swagger docs** at http://localhost:8000/docs
- **PostgreSQL** at localhost:5432

The React dashboard is a separate Vite app — see below.

### Manual Setup

See [COMMANDES.md](COMMANDES.md) for full Windows & Linux instructions.

```bash
# 1. Backend (Terminal 1)
cd backend
python -m venv .venv
.\.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # Linux/Mac
pip install -r requirements-dev.txt
cp ..\.env.example .env
alembic upgrade head
python -m scripts.generate_demo_data
uvicorn app.main:app --reload --port 8000

# 2. Frontend React (Terminal 2)
cd frontend
npm install
npm run dev        # http://localhost:5173
```


## Generate Demo Data

```bash
cd backend
python -m scripts.generate_demo_data
```

## Run Tests

```bash
cd backend
pytest -v
```

## Architecture

```
open-analytics-ai/
├── backend/          # FastAPI REST API + Analytics Engine
├── frontend/         # React dashboard (Vite + Tailwind + Recharts)
├── docs/             # Documentation
└── docker-compose.yml
```

See [docs/architecture.md](docs/architecture.md) for detailed architecture.

## API Usage

```javascript
const response = await fetch("http://localhost:8000/api/v1/analyze", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "X-API-Key": "YOUR_API_KEY"
  },
  body: JSON.stringify({
    application_slug: "my-app",
    dataset_slug: "my-dataset",
    analysis: ["summary", "trend", "anomaly"],
    data: [...]
  })
});
const result = await response.json();
```

See [docs/developer-integration.md](docs/developer-integration.md) for full integration guide.

## Roadmap

- **V1** (current): Data Registry, Validation, Analytics, Insights, React dashboard
- **V2**: Machine Learning, Advanced Anomaly Detection, Forecasting
- **V3**: Local Open Source LLM, Natural Language Analysis
- **V4**: React SDK, Easy Integration

## License

Internal use only.
