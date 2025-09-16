# RUNBOOK – Hybrid AI Platform

This runbook covers common operational tasks: health checks, database recovery, and migrations.

## Health & Readiness

-   **Liveness**: `GET /health` → `{"status":"ok"}`
-   **Readiness**: `GET /readiness` → checks DB within ~1.5s and returns:
    -   `{"status":"ok"}`
    -   or `{"status":"error","details":{"db":"error: <Type>"}}`

Use readiness for load balancers / K8s `readinessProbe`.

## Environment

-   **DB**: `${APP_DB_URL}` (asyncpg), defaults in CI to `postgresql+asyncpg://postgres:postgres@localhost:5432/app`
-   **Migrations**: `alembic` configured via `alembic.ini`
-   **App env**: `.env` (see README for full keys)

## Common Tasks

### 1) Drop & Recreate Database (Local)

> **Warning**: destructive. Ensure you're not pointing at production.

```bash
export PGHOST=localhost PGUSER=postgres PGPASSWORD=postgres PGDATABASE=postgres
# Drop and recreate 'app' db
psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='app';" || true
psql -c "DROP DATABASE IF EXISTS app;"
psql -c "CREATE DATABASE app OWNER postgres;"
```

### 2) Full Migraiton Reset (Alembic)

Reset all tables and reapply migrations from scratch:

```bash
# From repo root
python -m alembic downgrade base
python -m alembic upgrade head
```

### 3) Clean Tables (Keep Schema)

**Caution:** wipes data only, schema remains intact.

```bash
python - <<'PY'
import asyncio
from sqlalchemy import text
from src.db.session import async_session_maker  # adjust path if needed

async def main():
    async with async_session_maker() as s:
        await s.execute(text("TRUNCATE TABLE bookings, sentiments RESTART IDENTITY CASCADE;"))
        await s.commit()

asyncio.run(main())
PY
```

### 4) Verify Health

```bash
curl -sf localhost:8000/health
curl -sf localhost:8000/readiness | jq .
```

### 5) Troubleshooting

-   **Readiness error "timeout"** → DB not reachable or connection pool exhausted.
-   **Migrations fail** → check Alembic revision heads: python -m alembic history
-   **SSL / DSN issues** → verify DATABASE_URL / APP_DB_URL and driver (+asyncpg) correctness.

## Scripts

See scripts/ for helpers you can run safely in local/dev:

-   scripts/db_reset.sh → drop/recreate DB and reapply migrations
-   scripts/db_cleanup.sh → truncate core tables
