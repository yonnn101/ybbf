"""Infrastructure: JWT and auth-related settings (pydantic-settings)."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    """Secrets and token lifetime; set JWT_SECRET_KEY in production."""

    jwt_secret_key: str = Field(
        default="dev-only-change-with-JWT_SECRET_KEY",
        validation_alias="JWT_SECRET_KEY",
    )
    jwt_algorithm: str = Field(default="HS256", validation_alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=60,
        validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES",
    )
    access_token_cookie_name: str = Field(
        default="access_token",
        validation_alias="ACCESS_TOKEN_COOKIE_NAME",
    )
    cookie_secure: bool = Field(
        default=False,
        validation_alias="COOKIE_SECURE",
        description="Set True behind HTTPS so browsers send the auth cookie only over TLS.",
    )
    superuser_email: str | None = Field(default=None, validation_alias="SUPERUSER_EMAIL")
    superuser_password: str | None = Field(default=None, validation_alias="SUPERUSER_PASSWORD")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_auth_settings() -> AuthSettings:
    """Cached auth settings (one instance per process)."""
    return AuthSettings()


def bootstrap_superuser_enabled(cfg: AuthSettings) -> bool:
    """True when both email and a sufficiently long password are configured."""
    email = (cfg.superuser_email or "").strip()
    password = cfg.superuser_password or ""
    return bool(email) and len(password) >= 8
