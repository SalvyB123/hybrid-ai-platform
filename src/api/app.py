from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, Dict

# src/api/app.py
from fastapi import FastAPI
from src.api.routes.bookings import router as bookings_router

def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(bookings_router)
    return app

app = create_app()

from sqlalchemy import text

from src.config.settings import get_settings
from src.db.session import dispose_engine, engine

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    App lifecycle:
    - Startup: (hook for warmups, migrations triggers, cache, etc.)
    - Shutdown: dispose SQLAlchemy engine cleanly.
    """
    # --- startup work (optional) ---
    # e.g., ping DB once, warm caches, load config, etc.
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        # We don't fail the app on cold start if DB isn't up yet;
        # the /health endpoint will surface status.
        pass

    yield

    # --- shutdown work ---
    await dispose_engine()


app = FastAPI(title="Hybrid AI Platform", lifespan=lifespan)


@app.get("/health")
async def health() -> Dict[str, Any]:
    """
    Basic health endpoint:
    - reports environment
    - reports DB connectivity (best-effort, non-fatal)
    """
    db_ok = False
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            db_ok = result.scalar_one() == 1
    except Exception:
        db_ok = False

    return {
        "status": "ok" if db_ok else "degraded",
        "env": settings.app_env,
        "db": "up" if db_ok else "down",
    }
