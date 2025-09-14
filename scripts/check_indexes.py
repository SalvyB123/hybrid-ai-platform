# scripts/check_indexes.py
from __future__ import annotations

import asyncio
import os

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine

TABLE = "sentiment"


def _resolve_db_url() -> str:
    # Prefer async URLs first
    url = os.getenv("DATABASE_URL") or os.getenv("DATABASE_ASYNC_URL") or os.getenv("APP_DB_URL")
    if url:
        return url

    # Assemble from parts (defaults align with .env.example)
    user = os.getenv("APP_DB_USER", "appuser")
    pw = os.getenv("APP_DB_PASSWORD", "apppass")
    host = os.getenv("APP_DB_HOST", "localhost")
    port = os.getenv("APP_DB_PORT", "5432")
    name = os.getenv("APP_DB_NAME", "appdb")
    return f"postgresql+asyncpg://{user}:{pw}@{host}:{port}/{name}"


async def main() -> None:
    db_url = _resolve_db_url()
    engine = create_async_engine(db_url, future=True)
    try:
        async with engine.connect() as conn:

            def _inspect(sync_conn):
                insp = sa.inspect(sync_conn)
                return insp.get_indexes(TABLE)

            indexes = await conn.run_sync(_inspect)
        print(f"Indexes on '{TABLE}':")
        for idx in indexes:
            print(f"- name={idx.get('name')} columns={idx.get('column_names')}")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
