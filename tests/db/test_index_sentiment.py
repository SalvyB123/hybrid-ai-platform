import asyncio
import os

import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import create_async_engine

INDEX_NAME = "ix_sentiment_label_created_at"
TABLE_NAME = "sentiment"


def _resolve_db_url() -> str:
    """
    Resolve an async Postgres URL from environment, with sensible fallbacks.
    Mirrors the behaviour we use in scripts so the test runs in CI and locally.
    """
    url = os.getenv("DATABASE_URL") or os.getenv("DATABASE_ASYNC_URL") or os.getenv("APP_DB_URL")
    if url:
        return url

    user = os.getenv("APP_DB_USER", "appuser")
    pw = os.getenv("APP_DB_PASSWORD", "apppass")
    host = os.getenv("APP_DB_HOST", "localhost")
    port = os.getenv("APP_DB_PORT", "5432")
    name = os.getenv("APP_DB_NAME", "appdb")
    return f"postgresql+asyncpg://{user}:{pw}@{host}:{port}/{name}"


async def _list_indexes(db_url: str):
    engine = create_async_engine(db_url, future=True)
    try:
        async with engine.connect() as conn:

            def _inspect(sync_conn):
                insp = sa.inspect(sync_conn)
                return insp.get_indexes(TABLE_NAME)

            return await conn.run_sync(_inspect)
    finally:
        await engine.dispose()


def test_sentiment_index_exists_and_downgrades_cleanly():
    """
    - Upgrade to head: index must exist
    - Downgrade one revision: index must be gone
    - Upgrade back to head: index exists again
    """
    # Configure Alembic
    cfg = Config()
    cfg.set_main_option("script_location", "src/db/migrations")
    db_url = _resolve_db_url()
    cfg.set_main_option("sqlalchemy.url", db_url)  # async URL; env.py handles it

    # Upgrade to latest
    command.upgrade(cfg, "head")
    idx = asyncio.run(_list_indexes(db_url))
    names = {i["name"] for i in idx}
    assert INDEX_NAME in names, f"{INDEX_NAME} not found after upgrade; got {names}"

    # Downgrade one revision (the index migration) and verify removal
    command.downgrade(cfg, "-1")
    idx = asyncio.run(_list_indexes(db_url))
    names = {i["name"] for i in idx}
    assert INDEX_NAME not in names, f"{INDEX_NAME} still present after downgrade; got {names}"

    # Bring schema back to head for subsequent tests
    command.upgrade(cfg, "head")
