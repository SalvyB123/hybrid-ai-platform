# tests/integration/test_sentiment_unhappy.py
from __future__ import annotations

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from sqlalchemy.exc import SQLAlchemyError

from src.api.app import app
from src.api.routes.sentiment import SentimentRequest


@pytest.mark.asyncio
async def test_empty_text_returns_422() -> None:
    """
    Empty or whitespace-only text should fail request validation (422).
    """
    transport = ASGITransport(app=app)
    async with LifespanManager(app):
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            r = await client.post("/sentiment", json={"text": ""})
    assert r.status_code == 422
    body = r.json()
    assert body.get("error", {}).get("type") == "validation_error"
    assert "X-Request-ID" in r.headers


@pytest.mark.asyncio
async def test_very_long_text_returns_422_when_exceeds_limit() -> None:
    """
    Text over the maximum allowed length should be rejected by pydantic validation.
    """
    # Match the max_length we enforce in the request model
    max_len = getattr(SentimentRequest.model_fields["text"].annotation, "max_length", 2000)
    payload = {"text": "a" * (max_len + 1)}
    transport = ASGITransport(app=app)
    async with LifespanManager(app):
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            r = await client.post("/sentiment", json=payload)
    assert r.status_code == 422
    body = r.json()
    assert body.get("error", {}).get("type") == "validation_error"
    assert "X-Request-ID" in r.headers


@pytest.mark.asyncio
async def test_db_failure_returns_500_and_error_envelope(monkeypatch) -> None:
    """
    Simulate a DB failure on commit and ensure we return a 500 with the standard error envelope.
    """
    transport = ASGITransport(app=app)
    async with LifespanManager(app):
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:

            # Monkeypatch the AsyncSession.commit used by the route dependency
            from src.api.routes import sentiment as sentiment_route_module

            async def boom(*args, **kwargs):
                raise SQLAlchemyError("simulated failure")

            monkeypatch.setattr(
                sentiment_route_module, "AsyncSession", sentiment_route_module.AsyncSession
            )
            # Patch the bound method on the instance via context manager in route:
            # We'll patch the commit method on the class so any instance commit() explodes.
            from sqlalchemy.ext.asyncio import AsyncSession as _AsyncSession

            monkeypatch.setattr(_AsyncSession, "commit", boom, raising=True)

            r = await client.post("/sentiment", json={"text": "this will fail to persist"})

    # Expect global error handler to map to 500 with JSON envelope and request ID
    assert r.status_code == 500
    body = r.json()
    assert body.get("error", {}).get("type") == "internal_server_error"
    assert "X-Request-ID" in r.headers
