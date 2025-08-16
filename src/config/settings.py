"""App settings placeholder (env parsing goes here)."""

import os


class Settings:
    ENV: str = os.getenv("ENV", "local")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"


settings = Settings()
