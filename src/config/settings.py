# src/config/settings.py
from __future__ import annotations

from functools import lru_cache

from pydantic import ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- FAQ Bot ---
    faq_confidence_threshold: float = 0.60

    # --- General ---
    app_env: str = "local"
    debug: bool = True

    # --- Database ---
    app_db_user: str = "appuser"
    app_db_password: str = "apppass"
    app_db_name: str = "appdb"
    app_db_host: str = "localhost"
    app_db_port: int = 5432
    app_db_url: str | None = None  # optional override (takes precedence)

    # --- Optional pgAdmin ---
    pgadmin_email: str | None = None
    pgadmin_password: str | None = None

    # --- Email handoff ---
    smtp_host: str | None = None
    smtp_port: int | None = None
    smtp_from: str | None = None
    handoff_to: str | None = None

    # --- CORS ---
    # Accepts either JSON (["http://a","http://b"]) or comma-separated (http://a,http://b)
    cors_allowed_origins: list[str] = ["http://localhost:5173"]

    # --- Settings config ---
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("app_db_url", mode="before")
    @classmethod
    def assemble_db_url(cls, v: str | None, info: ValidationInfo) -> str:
        if v:
            return v
        data = info.data
        user = data.get("app_db_user", "appuser")
        pw = data.get("app_db_password", "apppass")
        host = data.get("app_db_host", "localhost")
        port = data.get("app_db_port", 5432)
        name = data.get("app_db_name", "appdb")
        return f"postgresql+asyncpg://{user}:{pw}@{host}:{port}/{name}"

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def parse_origins(cls, v):
        """
        Allow both JSON arrays and comma-separated strings for env input.
        pydantic-settings will already try JSON; if that fails or it's a plain string,
        handle comma-separated gracefully.
        """
        if v is None:
            return v
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            # If someone passed a JSON array string, leave it to the JSON parser upstream.
            # But if we get here as a plain string, split on commas.
            if v.strip().startswith("["):
                return v  # let the built-in JSON parsing handle it
            # comma-separated
            parts = [s.strip() for s in v.split(",") if s.strip()]
            return parts or ["http://localhost:5173"]
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()
