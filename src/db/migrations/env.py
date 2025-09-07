from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from src.db.session import Base  # Base.metadata must exist for autogenerate
from src.db import models  # noqa: F401  # ensure models are imported for autogenerate
from src.config.settings import Settings

# Alembic Config
config = context.config

# Configure logging via alembic.ini if present
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for 'autogenerate' support
target_metadata = Base.metadata


def _get_db_url() -> str:
    """
    Prefer URL provided by Alembic (e.g. tests set sqlalchemy.url to the test DB),
    otherwise fall back to application settings.
    """
    cfg_url = config.get_main_option("sqlalchemy.url")
    if cfg_url:
        return cfg_url
    return Settings().app_db_url  # e.g. postgresql+asyncpg://user:pass@host:5432/db


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (emit SQL without an Engine)."""
    context.configure(
        url=_get_db_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def _do_run_migrations(connection) -> None:
    """Configure Alembic and run migrations using a *sync* connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode using an async Engine."""
    connectable: AsyncEngine = create_async_engine(
        _get_db_url(),
        poolclass=pool.NullPool,
        pool_pre_ping=True,
        future=True,
    )
    try:
        async with connectable.connect() as connection:
            # run the sync migration logic within the async connection
            await connection.run_sync(_do_run_migrations)
    finally:
        await connectable.dispose()


def _run_async(coro) -> None:
    # Alembic invokes env.py in a normal (non-async) context.
    # Using asyncio.run here is fine; in tests we call Alembic in a worker thread.
    asyncio.run(coro)


if context.is_offline_mode():
    run_migrations_offline()
else:
    _run_async(run_migrations_online())
