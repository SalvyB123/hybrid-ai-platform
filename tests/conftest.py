from __future__ import annotations

import asyncio
import os
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from asgi_lifespan import LifespanManager
from alembic import command
from alembic.config import Config

from src.api.app import create_app
from src.db.session import get_db
from src.config.settings import Settings


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

TEST_DB_NAME = os.getenv("APP_DB_NAME_TEST", "appdb_test")


def _server_url() -> str:
    """Connect to the server-level 'postgres' DB for CREATE/DROP DATABASE."""
    s = Settings()
    return (
        f"postgresql+asyncpg://{s.app_db_user}:{s.app_db_password}"
        f"@{s.app_db_host}:{s.app_db_port}/postgres"
    )


def _build_test_db_url() -> str:
    """Async URL for the test database itself."""
    s = Settings()
    return (
        f"postgresql+asyncpg://{s.app_db_user}:{s.app_db_password}"
        f"@{s.app_db_host}:{s.app_db_port}/{TEST_DB_NAME}"
    )


# ---------------------------------------------------------------------------
# DB bootstrap helpers (AUTOCOMMIT, no transaction for CREATE/DROP DATABASE)
# ---------------------------------------------------------------------------


async def _create_database_if_missing() -> None:
    """
    Ensure the test DB exists.
    - Uses AUTOCOMMIT and a plain connection (no transaction).
    - SQLAlchemy 2.0 compatible API.
    """
    engine = create_async_engine(_server_url(), isolation_level="AUTOCOMMIT")
    async with engine.connect() as conn:
        # Check if it exists (normal text() execution is fine here)
        res = await conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": TEST_DB_NAME},
        )
        exists = res.scalar() is not None
        if not exists:
            # CREATE DATABASE must not run in a transaction block
            await conn.exec_driver_sql(f'CREATE DATABASE "{TEST_DB_NAME}"')
    await engine.dispose()


async def _drop_database() -> None:
    """
    Drop the test DB.
    - Terminates active connections first.
    - Uses AUTOCOMMIT with a plain connection (no transaction).
    """
    engine = create_async_engine(_server_url(), isolation_level="AUTOCOMMIT")
    async with engine.connect() as conn:
        # exec_driver_sql doesn't support named params with asyncpg; inline safely
        await conn.exec_driver_sql(
            f"SELECT pg_terminate_backend(pid) "
            f"FROM pg_stat_activity WHERE datname = '{TEST_DB_NAME}'"
        )
        await conn.exec_driver_sql(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}"')
    await engine.dispose()


# ---------------------------------------------------------------------------
# Pytest configuration and fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def anyio_backend():
    # Ensure AnyIO/pytest-asyncio use asyncio
    return "asyncio"


@pytest.fixture(scope="session")
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Session-scoped async engine bound to the test database.
    Creates the DB if missing, and drops it at the end of the test session.
    """
    await _create_database_if_missing()
    engine = create_async_engine(_build_test_db_url(), future=True, echo=False)
    try:
        yield engine
    finally:
        await engine.dispose()
        await _drop_database()


@pytest.fixture(scope="session")
async def apply_migrations(test_engine: AsyncEngine):
    """
    Run Alembic migrations to head against the test DB.
    We set both script_location and sqlalchemy.url explicitly, and
    execute Alembic in a background thread to avoid asyncio.run() conflicts.
    """
    # Build a config without relying on alembic.ini defaults
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", "src/db/migrations")
    alembic_cfg.set_main_option("sqlalchemy.url", _build_test_db_url())
    # Optional: make Alembic logging quieter
    alembic_cfg.set_main_option("stdout", "false")

    loop = asyncio.get_running_loop()
    # Run `alembic upgrade head` in a thread (env.py uses asyncio.run)
    await loop.run_in_executor(None, command.upgrade, alembic_cfg, "head")

    # --- sanity check: ensure the bookings table exists after upgrade ---
    async with test_engine.connect() as conn:
        res = await conn.execute(
            text("SELECT to_regclass('public.bookings') IS NOT NULL AS exists_flag")
        )
        exists = bool(res.scalar())
        if not exists:
            # Helpful diagnostics for quick triage
            # Print current revision and history using Alembic API in thread
            def _print_history():
                print("== Alembic current ==")
                command.current(alembic_cfg, verbose=True)
                print("== Alembic history ==")
                command.history(alembic_cfg, verbose=True)

            await loop.run_in_executor(None, _print_history)
            raise RuntimeError(
                "Alembic upgrade did not create 'bookings' table in the test DB. "
                "Check your migration files and script_location."
            )

    return True


@pytest.fixture
async def db_session(
    test_engine: AsyncEngine, apply_migrations
) -> AsyncGenerator[AsyncSession, None]:
    """
    Function-scoped AsyncSession for tests.
    We yield the session and roll back after each test for hygiene.
    """
    SessionLocal = async_sessionmaker(bind=test_engine, expire_on_commit=False, class_=AsyncSession)
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            # Safety: API code usually commits; ensure no leaked tx state.
            await session.rollback()


@pytest.fixture
async def test_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    FastAPI client with dependency override so requests use the test session
    (i.e., the test DB) rather than your dev DB.
    """
    app = create_app()

    async def _get_test_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = _get_test_db

    # Ensure FastAPI startup/shutdown runs
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            yield client
