from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from src.api.errors import install_error_handlers
from src.api.middleware.request_context import RequestContextMiddleware
from src.api.routes import health as health_routes
from src.api.routes.bookings import router as bookings_router
from src.api.routes.faq import router as faq_router
from src.api.routes.sentiment import router as sentiment_router
from src.common.json_logging import setup_json_logging
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
    # Configure JSON logging once
    setup_json_logging(level="INFO" if not settings.debug else "DEBUG")

    # --- startup work (optional) ---
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        # Don't fail the app on cold start if DB isn't up yet;
        # the /health endpoint will surface status.
        pass

    yield

    # --- shutdown work ---
    await dispose_engine()


def create_app() -> FastAPI:
    app = FastAPI(title="Hybrid AI Platform", lifespan=lifespan)

    # --- Request context / access logs ---
    app.add_middleware(RequestContextMiddleware)

    # --- CORS: explicit allow-list (enterprise default) ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        allow_credentials=True,
        max_age=600,
    )

    # Mount routers
    app.include_router(bookings_router)
    app.include_router(faq_router)
    app.include_router(sentiment_router)
    app.include_router(health_routes.router)

    # Error handlers (consistent JSON envelope)
    install_error_handlers(app)

    @app.get("/health")
    async def health() -> dict[str, Any]:
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

    return app


app = create_app()
