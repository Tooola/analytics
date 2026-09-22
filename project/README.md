# Open Analytics AI

Analytics and AI interpretation platform for multi-application environments.

## Overview

Open Analytics AI is a reusable backend that provides analytics, trend analysis, anomaly detection, and AI-powered insights to React applications via a REST API.

**Supported client applications**: Farmtinz, CRMtinz, Sharetinz, and any future apps.

## Quick Start

### Using Docker (recommended)

```bash
docker compose up
```

This starts:
- **FastAPI** at http://localhost:8000
- **Swagger docs** at http://localhost:8000/docs
- **Streamlit dashboard** at http://localhost:8501
- **PostgreSQL** at localhost:5432

### Manual Setup

See [COMMANDES.md](COMMANDES.md) for full Windows & Linux instructions.

```bash
# 1. Backend (Terminal 1)
cd backend
python -m venv .venv
.\.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
cp ..\.env.example .env
alembic upgrade head
python -m scripts.generate_demo_data
uvicorn app.main:app --reload --port 8000

# 2. Dashboard (Terminal 2)
cd dashboard
..\backend\.venv\Scripts\python.exe -m streamlit run app.py
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
├── dashboard/        # Streamlit admin/testing UI
├── docker/           # Docker configuration
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

- **V1** (current): Data Registry, Validation, Analytics, Insights, Streamlit
- **V2**: Machine Learning, Advanced Anomaly Detection, Forecasting
- **V3**: Local Open Source LLM, Natural Language Analysis
- **V4**: React SDK, Easy Integration

## License

Internal use only.
