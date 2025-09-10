from __future__ import annotations

import asyncio
import os
import smtplib
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.api.app import create_app
from src.config.settings import Settings
from src.db.session import get_db

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
        res = await conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": TEST_DB_NAME},
        )
        exists = res.scalar() is not None
        if not exists:
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
        await conn.exec_driver_sql(
            f"SELECT pg_terminate_backend(pid) "
            f"FROM pg_stat_activity WHERE datname = '{TEST_DB_NAME}'"
        )
        await conn.exec_driver_sql(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}"')
    await engine.dispose()


# ---------------------------------------------------------------------------
# Pytest configuration and fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture(scope="function")
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


@pytest_asyncio.fixture(scope="function")
async def apply_migrations(test_engine: AsyncEngine):
    """
    Run Alembic migrations to head against the test DB.
    We set both script_location and sqlalchemy.url explicitly, and
    execute Alembic in a background thread to avoid asyncio.run() conflicts.
    """
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", "src/db/migrations")
    alembic_cfg.set_main_option("sqlalchemy.url", _build_test_db_url())
    alembic_cfg.set_main_option("stdout", "false")

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, command.upgrade, alembic_cfg, "head")

    async with test_engine.connect() as conn:
        res = await conn.execute(
            text("SELECT to_regclass('public.bookings') IS NOT NULL AS exists_flag")
        )
        exists = bool(res.scalar())
        if not exists:

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


@pytest_asyncio.fixture
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
            await session.rollback()


@pytest_asyncio.fixture
async def test_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    FastAPI client with dependency override so requests use the test session
    (i.e., the test DB) rather than your dev DB.
    """
    app = create_app()

    async def _get_test_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = _get_test_db

    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            yield client


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the entire test session."""
    loop = asyncio.new_event_loop()
    try:
        yield loop
    finally:
        loop.close()


# --- Global safety: never touch real SMTP in tests ---
@pytest.fixture(autouse=True)
def _mock_smtp_and_email_handoff(monkeypatch):
    """
    Ensure no test can hit a real SMTP server.

    - Clear SMTP-related env vars.
    - Replace smtplib.SMTP with a dummy.
    - Replace send_handoff_email at both the notify module and the router import site.
      (Individual tests can still override with their own monkeypatch.)
    """
    for k in ("SMTP_HOST", "SMTP_PORT", "SMTP_FROM", "HANDOFF_TO"):
        os.environ.pop(k, None)

    class _DummySMTP:
        def __init__(self, *a, **kw): ...

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def send_message(self, *a, **kw):
            return None

    monkeypatch.setattr(smtplib, "SMTP", _DummySMTP, raising=True)

    # No-op email sender
    def _noop(*args, **kwargs):
        return True

    try:
        import src.ai.faq.notify as notify_mod

        monkeypatch.setattr(notify_mod, "send_handoff_email", _noop, raising=False)
    except Exception:
        pass

    try:
        import src.api.routes.faq as faq_mod

        monkeypatch.setattr(faq_mod, "send_handoff_email", _noop, raising=False)
    except Exception:
        pass

    return None
