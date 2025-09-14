import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient

from src.api.app import app


@pytest.mark.asyncio
async def test_validation_error_and_request_id_header():
    # Hit /sentiment with an empty body to trigger validation error
    async with LifespanManager(app):
        async with AsyncClient(transport=None, base_url="http://testserver") as client:
            r = await client.post("/sentiment", json={})  # missing required fields
    assert r.status_code == 422
    assert "X-Request-ID" in r.headers
    data = r.json()
    assert "error" in data and data["error"]["type"] == "validation_error"
    assert data["error"]["request_id"] == r.headers["X-Request-ID"]
