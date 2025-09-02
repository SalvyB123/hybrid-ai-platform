from functools import lru_cache
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Read from .env; ignore unexpected keys to be resilient
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",  # <- important: don't error on unrelated env vars
    )

    # General
    app_env: str = "local"  # maps to APP_ENV
    debug: bool = True  # maps to DEBUG

    # DB pieces
    app_db_user: str = "appuser"
    app_db_password: str = "apppass"
    app_db_name: str = "appdb"
    app_db_host: str = "localhost"
    app_db_port: int = 5432
    app_db_url: str | None = None  # optional override

    # Optional pgAdmin (present in .env for docker-compose)
    pgadmin_email: str | None = None  # maps to PGADMIN_EMAIL
    pgadmin_password: str | None = None  # maps to PGADMIN_PASSWORD

    @field_validator("app_db_url", mode="before")
    @classmethod
    def assemble_db_url(cls, v: str | None, values: dict):
        if v:
            return v
        user = values.get("app_db_user")
        pw = values.get("app_db_password")
        host = values.get("app_db_host")
        port = values.get("app_db_port")
        name = values.get("app_db_name")
        return f"postgresql+asyncpg://{user}:{pw}@{host}:{port}/{name}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
