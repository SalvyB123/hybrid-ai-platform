from __future__ import annotations

import uuid

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from src.api.app import app
from src.db.models.sentiment import Sentiment
from src.db.session import AsyncSessionLocal


@pytest.mark.asyncio
async def test_post_sentiment_returns_json_201() -> None:
    transport = ASGITransport(app=app)
    async with LifespanManager(app):
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            payload = {"text": "Support was helpful and great value."}
            resp = await client.post("/sentiment", json=payload)
            assert resp.status_code == 201, resp.text

            data = resp.json()
            assert set(data.keys()) == {"id", "text", "score", "label"}
            uuid.UUID(data["id"])
            assert data["text"] == payload["text"]
            assert isinstance(data["score"], float)
            assert data["label"] in {"positive", "negative", "neutral"}


@pytest.mark.asyncio
async def test_post_sentiment_persists_to_db() -> None:
    transport = ASGITransport(app=app)
    async with LifespanManager(app):
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            payload = {"text": "Setup was quick… not."}
            resp = await client.post("/sentiment", json=payload)
            assert resp.status_code == 201, resp.text
            created = resp.json()

    # Verify persistence in DB
    async with AsyncSessionLocal() as session:
        stmt = select(Sentiment).where(Sentiment.id == uuid.UUID(created["id"]))
        result = await session.execute(stmt)
        row = result.scalar_one()

        assert row.text == payload["text"]
        assert isinstance(row.score, float)
        assert row.label in {"positive", "negative", "neutral"}
