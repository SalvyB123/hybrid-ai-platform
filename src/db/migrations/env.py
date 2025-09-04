import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

# Your app imports
from src.config.settings import Settings
from src.db.session import Base  # Base.metadata must exist
from src.db import models  # noqa: F401

# Alembic Config
config = context.config

# Logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for autogenerate
target_metadata = Base.metadata

# Build DB URL from settings (async)
settings = Settings()
ASYNC_DB_URL = settings.app_db_url  # e.g. postgresql+asyncpg://user:pass@host:5432/db


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (emit SQL)."""
    context.configure(
        url=ASYNC_DB_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Configure Alembic and run migrations using a *sync* connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode using an async engine."""
    connectable = create_async_engine(ASYNC_DB_URL, pool_pre_ping=True)

    async with connectable.connect() as connection:
        # IMPORTANT: both configure + run_migrations happen inside run_sync
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_async(fn):
    asyncio.run(fn())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_async(run_migrations_online)
