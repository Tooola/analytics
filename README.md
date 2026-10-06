# analytics

[![CI](https://github.com/Tooola/analytics/actions/workflows/ci.yml/badge.svg)](https://github.com/Tooola/analytics/actions/workflows/ci.yml)

**Open Analytics AI** — un backend d'analytics réutilisable (FastAPI + dashboard Streamlit) qui transforme vos données JSON en statistiques, tendances, détections d'anomalies et interprétations IA via une simple API REST.
Conçu pour les équipes multi-applications (Farmtinz, CRMtinz, Sharetinz, …) : chaque application branche l'analyse et l'IA avec sa propre clé API, sans les réimplémenter.

## Démarrage rapide

```bash
git clone https://github.com/Tooola/analytics.git
cd analytics/project
docker compose up
```

- API FastAPI : <http://localhost:8000> · Swagger : <http://localhost:8000/docs>
- Dashboard Streamlit : <http://localhost:8501>
- Sans Docker : [installation manuelle](project/README.md#quick-start)

> Backend de démo : <https://scintillating-kindness-production-d038.up.railway.app>

## Tests

```bash
cd project/backend
pip install -r requirements-dev.txt
pytest
```

## Documentation

| Document | Contenu |
|---|---|
| [project/README.md](project/README.md) | Présentation, architecture, usage de l'API |
| [Guide d'intégration développeur](project/docs/DEVELOPER_INTEGRATION_GUIDE.md) | Brancher votre application (FR) |
| [Developer integration](project/docs/developer-integration.md) | Intégration & sécurité (EN) |
| [api.md](project/docs/api.md) | Référence des endpoints |
| [architecture.md](project/docs/architecture.md) | Architecture technique |
| [Railway & kit collègues](project/docs/RAILWAY_ET_KIT_COLLEGUES.md) | Déploiement + fiche à donner aux collègues |
| [PLAN.md](PLAN.md) | Plan d'implémentation (jours 1-7) |
