import asyncio
import os

import asyncpg

DB_URL = os.environ.get("DATABASE_URL")
if not DB_URL:
    raise SystemExit("❌ DATABASE_URL not set")

# asyncpg expects postgresql:// (not postgresql+asyncpg://)
DB_URL = DB_URL.replace("+asyncpg", "")

SQL = "DROP TABLE IF EXISTS sentiment CASCADE;"


async def main():
    conn = await asyncpg.connect(dsn=DB_URL)
    try:
        await conn.execute(SQL)
        print("✅ Dropped table: sentiment")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
