import pytest
from httpx import AsyncClient, ASGITransport

from src.api.app import app


@pytest.mark.anyio("asyncio")
async def test_health_ok():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@pytest.mark.anyio("asyncio")
async def test_readiness_ok():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/readiness")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"


@pytest.mark.anyio("asyncio")
async def test_readiness_db_error(monkeypatch):
    from sqlalchemy.ext.asyncio import AsyncSession

    async def broken_execute(self, *args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(AsyncSession, "execute", broken_execute, raising=True)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/readiness")
    assert r.status_code == 200  # JSON body encodes error status
    body = r.json()
    assert body["status"] == "error"
    assert "db" in (body.get("details") or {})