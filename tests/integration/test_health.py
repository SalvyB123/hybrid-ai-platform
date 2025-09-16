import pytest
from httpx import AsyncClient

from src.api.app import app  # adjust if your app object lives elsewhere

@pytest.mark.anyio
async def test_health_ok():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

@pytest.mark.anyio
async def test_readiness_ok(db_session_ready):  # if you have a fixture, else drop param
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/readiness")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"

# Optionally: simulate DB failure by monkeypatching session.execute to raise
@pytest.mark.anyio
async def test_readiness_db_error(monkeypatch):
    from sqlalchemy.ext.asyncio import AsyncSession

    async def broken_execute(self, *args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(AsyncSession, "execute", broken_execute, raising=True)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/readiness")
    assert r.status_code == 200  # probes usually 200 with status payload; platform reads JSON
    body = r.json()
    assert body["status"] == "error"
    assert "db" in (body.get("details") or {})