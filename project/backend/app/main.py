"""FastAPI application entry point."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import settings
from app.core.database import Base, engine
from app.core.logging import get_logger, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger = get_logger("app")
    logger.info("Starting %s in %s mode", settings.app_name, settings.app_env)
    # Create tables if they don't exist (dev convenience — use Alembic for prod)
    Base.metadata.create_all(bind=engine)
    yield
    logger.info("Shutting down %s", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    description=(
        "Analytics and AI interpretation platform. "
        "Register applications, declare datasets, submit data, "
        "and receive structured insights."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — origins are configured per-environment via CORS_ORIGINS env var.
# API calls from client backends (server-to-server) are not browser requests
# and are therefore not constrained by CORS. This middleware protects the
# Streamlit dashboard and any browser-based tooling only.
# NOTE: never use allow_credentials=True with allow_origins=["*"].
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-API-Key"],
)

# Register the v1 API router
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger = get_logger("app")
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "Internal server error"},
    )


@app.get("/")
def root() -> dict:
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "docs": "/docs",
        "api_prefix": settings.api_v1_prefix,
    }
