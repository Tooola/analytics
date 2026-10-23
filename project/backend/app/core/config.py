"""Application configuration loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        # Fail fast on unknown env keys (catches typos like GROQ_API_KEYY)
        # instead of silently running with defaults.
        extra="forbid",
    )

    # Application
    app_name: str = "Open Analytics AI"
    app_env: str = "development"
    # Safe default: verbose output must be an explicit opt-in via DEBUG=true.
    debug: bool = False

    # Database
    database_url: str = "sqlite:///./analytics.db"
    # Only consumed by docker-compose interpolation (the app reads
    # DATABASE_URL); declared here so a shared .env never trips
    # extra="forbid".
    postgres_password: str | None = None

    # API
    api_v1_prefix: str = "/api/v1"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Security
    # IMPORTANT: override this secret in production — never use the default.
    api_key_hash_secret: str = "change-me-in-production"
    api_key_prefix: str = "anal_"
    # Historical global ceiling (kept: local .env files set it). Concrete
    # limits are declared per-route on the expensive endpoints — see
    # app/core/ratelimit.py (a global default would throttle the dashboard).
    rate_limit_per_minute: int = 60

    # CORS — default allows all origins for seamless client integration.
    cors_origins: list[str] = ["*"]

    # AI Provider
    ai_provider: str = "mock"
    gemini_api_key: str | None = None
    groq_api_key: str | None = None
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"

    # Dashboard authentication (React login)
    # Accounts declared here are created at startup when missing (seeded).
    # Password must be set in production; login stays disabled without it.
    dashboard_admin_username: str | None = None
    dashboard_admin_password: str | None = None
    dashboard_token_expire_minutes: int = 720  # 12h
    # Login brute-force protection (attempts/minute per client bucket).
    # The test suite raises this so fixtures never trip the limiter.
    dashboard_login_per_minute: int = 5

    # Consolidated multi-dataset analysis (POST /analyze/multi) is heavier
    # than a single run — tighter default than /analyze (20/min). Tests
    # raise it via ANALYZE_MULTI_PER_MINUTE.
    analyze_multi_per_minute: int = 10

    # Registration throttles — tests raise both so fixtures never trip the
    # limiter (many apps/datasets are registered within one minute). The
    # suite keeps POST /analyze hard-coded: a security test asserts 429.
    applications_create_per_minute: int = 15
    datasets_create_per_minute: int = 30

    # Legacy dashboard leftovers — kept only so existing .env files keep
    # loading (Settings uses extra="forbid"); nothing reads them anymore.
    dashboard_port: int = 8501
    api_base_url: str = "http://localhost:8000"

    from pydantic import model_validator

    @model_validator(mode="after")
    def validate_production_secrets(self) -> Settings:
        if self.app_env.lower() not in ("development", "dev", "test") and self.api_key_hash_secret == "change-me-in-production":
            raise ValueError("API_KEY_HASH_SECRET must be configured in non-development environment")
        return self



@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
