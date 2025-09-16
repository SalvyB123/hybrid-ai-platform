#!/usr/bin/env bash
set -euo pipefail

echo ">> Truncating core tables (bookings, sentiments)"
python - <<'PY'
import asyncio
from sqlalchemy import text
from src.db.session import async_session_maker  # adjust path

async def main():
    async with async_session_maker() as s:
        await s.execute(text("TRUNCATE TABLE bookings, sentiments RESTART IDENTITY CASCADE;"))
        await s.commit()
asyncio.run(main())
PY
echo ">> Done."