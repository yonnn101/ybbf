"""Infrastructure: application settings loaded from environment (pydantic-settings)."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Process-wide config: database, Redis/Celery broker, optional object storage."""

    database_url: str = Field(validation_alias="DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379/0", validation_alias="REDIS_URL")
    minio_endpoint: str | None = Field(default=None, validation_alias="MINIO_ENDPOINT")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def get_app_settings() -> AppSettings:
    """Return cached settings instance (call once per process if desired)."""
    return AppSettings()
