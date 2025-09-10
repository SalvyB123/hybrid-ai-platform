# src/config/settings.py
from __future__ import annotations

from functools import lru_cache

from pydantic import ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- FAQ Bot ---
    # Confidence threshold in [0,1]
    faq_confidence_threshold: float = 0.60

    # --- General ---
    app_env: str = "local"  # maps from APP_ENV (case-insensitive)
    debug: bool = True  # maps from DEBUG

    # --- Database ---
    app_db_user: str = "appuser"
    app_db_password: str = "apppass"
    app_db_name: str = "appdb"
    app_db_host: str = "localhost"
    app_db_port: int = 5432
    app_db_url: str | None = None  # optional override (takes precedence)

    # --- Optional pgAdmin (docker compose) ---
    pgadmin_email: str | None = None
    pgadmin_password: str | None = None

    # --- Email handoff (used in the next task; safe to keep default/None now) ---
    smtp_host: str | None = None  # e.g. "localhost" for MailHog
    smtp_port: int | None = None  # e.g. 1025 for MailHog
    smtp_from: str | None = None  # e.g. "bot@local.test"
    handoff_to: str | None = None  # e.g. "founder@local.test"

    # --- Settings config ---
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,  # allow APP_ENV or app_env etc.
        extra="ignore",  # ignore unknown env vars
    )

    @field_validator("app_db_url", mode="before")
    @classmethod
    def assemble_db_url(cls, v: str | None, info: ValidationInfo) -> str:
        """If APP_DB_URL is not provided, build it from the individual parts."""
        if v:
            return v
        data = info.data
        user = data.get("app_db_user", "appuser")
        pw = data.get("app_db_password", "apppass")
        host = data.get("app_db_host", "localhost")
        port = data.get("app_db_port", 5432)
        name = data.get("app_db_name", "appdb")
        return f"postgresql+asyncpg://{user}:{pw}@{host}:{port}/{name}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
