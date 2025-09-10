from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from src.config.settings import get_settings


# ---- Declarative base for your ORM models ----
class Base(DeclarativeBase):
    """Base class for SQLAlchemy ORM models."""

    pass


# ---- Engine & Session Factory (module-level singletons) ----
_settings = get_settings()

# Create the async engine from env-driven URL, with sane defaults
engine: AsyncEngine = create_async_engine(
    _settings.app_db_url,
    echo=False,  # flip to True locally if you want SQL in logs
    pool_pre_ping=True,  # validates connections before using them
    future=True,  # SQLAlchemy 2.0 style
)

# Session factory; each request gets its own session
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,  # keeps attributes available after commit
    autoflush=False,
)


# ---- FastAPI dependency ----
async def get_db() -> AsyncIterator[AsyncSession]:
    """
    Yields an AsyncSession to endpoints/services.
    Ensures proper close even on exception.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            # session context manager already closes; explicit for clarity
            await session.close()


# ---- Optional graceful shutdown helpers ----
async def dispose_engine() -> None:
    """Call on app shutdown to close the engine cleanly."""
    await engine.dispose()
