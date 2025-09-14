import asyncio
import os

import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import create_async_engine

# The revision that *precedes* the sentiment table creation (bookings revision)
DOWNGRADE_TARGET_BEFORE_SENTIMENT = "1130532299a8"


def _get_async_db_url() -> str:

    url = os.getenv("DATABASE_URL") or os.getenv("DATABASE_ASYNC_URL")
    if url:
        return url
    # Fallback to app settings (works in local dev)
    from src.config.settings import get_settings

    return get_settings().app_db_url


def test_sentiment_migration_upgrade_downgrade_roundtrip():
    """
    Round-trip the latest migration that creates the 'sentiment' table:
      - upgrade head -> table exists with expected columns
      - downgrade to the revision *before* sentiment -> table gone
      - upgrade head -> table exists again
    """
    cfg = Config()
    cfg.set_main_option("script_location", "src/db/migrations")

    db_url = _get_async_db_url()
    cfg.set_main_option("sqlalchemy.url", db_url)  # keep async for env.py

    async def table_info():
        engine = create_async_engine(db_url, future=True)
        try:
            async with engine.connect() as conn:

                def _inspect(sync_conn):
                    insp = sa.inspect(sync_conn)
                    exists = insp.has_table("sentiment")
                    cols = []
                    if exists:
                        cols = [c["name"] for c in insp.get_columns("sentiment")]
                    return exists, cols

                exists, cols = await conn.run_sync(_inspect)
                return exists, cols
        finally:
            await engine.dispose()

    # Upgrade to head and assert presence
    command.upgrade(cfg, "head")
    exists, cols = asyncio.run(table_info())
    assert exists, "sentiment table should exist after upgrade head"
    for expected in {"id", "text", "score", "label", "created_at"}:
        assert expected in cols, f"missing column: {expected}"

    # Downgrade to the revision BEFORE the sentiment table existed -> table dropped
    command.downgrade(cfg, DOWNGRADE_TARGET_BEFORE_SENTIMENT)
    exists, _ = asyncio.run(table_info())
    assert not exists, "sentiment table should be dropped after downgrade to pre-sentiment revision"

    # Upgrade back to head and assert presence again
    command.upgrade(cfg, "head")
    exists, cols = asyncio.run(table_info())
    assert exists, "sentiment table should exist after upgrading back to head"
    for expected in {"id", "text", "score", "label", "created_at"}:
        assert expected in cols, f"missing column after re-upgrade: {expected}"
