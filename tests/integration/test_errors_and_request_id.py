import pytest
from httpx import ASGITransport, AsyncClient

from src.api.app import app


@pytest.mark.asyncio
async def test_validation_error_and_request_id_header():
    # Use ASGITransport to talk to the app in-process (no network)
    transport = ASGITransport(app=app, lifespan="on")
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        r = await client.post("/sentiment", json={})  # missing required fields

    assert r.status_code == 422
    assert "X-Request-ID" in r.headers
    data = r.json()
    assert "error" in data and data["error"]["type"] == "validation_error"
    assert data["error"]["request_id"] == r.headers["X-Request-ID"]
