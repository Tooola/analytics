"""Application configuration loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Open Analytics AI"
    app_env: str = "development"
    debug: bool = True

    # Database
    database_url: str = "sqlite:///./analytics.db"

    # API
    api_v1_prefix: str = "/api/v1"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Security
    # IMPORTANT: override this secret in production — never use the default.
    api_key_hash_secret: str = "change-me-in-production"
    api_key_prefix: str = "anal_"
    rate_limit_per_minute: int = 60

    # CORS — default allows all origins for seamless client integration.
    cors_origins: list[str] = ["*"]

    # AI Provider
    ai_provider: str = "mock"
    gemini_api_key: str | None = None
    groq_api_key: str | None = None
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"

    # Dashboard
    dashboard_port: int = 8501
    api_base_url: str = "http://localhost:8000"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
