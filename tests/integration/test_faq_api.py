import types
import numpy as np
import pytest
from httpx import AsyncClient
from httpx import ASGITransport  # NEW
from asgi_lifespan import LifespanManager

from src.api.app import app


@pytest.mark.asyncio
async def test_faq_ask_returns_answer(monkeypatch):
    import src.api.routes.faq as faq_mod

    class FakeEmbedder:
        def encode(self, texts):
            arr = [np.array([1.0, 0.0], dtype="float32") for _ in texts]
            return np.vstack(arr)

    faqs = [
        types.SimpleNamespace(
            id="faq-001", question="How do I book a demo?", answer="Use /bookings."
        ),
        types.SimpleNamespace(id="faq-002", question="Something else?", answer="Another answer."),
    ]
    doc_emb = np.array([[1.0, 0.0], [0.0, 1.0]], dtype="float32")

    monkeypatch.setattr(faq_mod, "_FAQS", faqs, raising=False)
    monkeypatch.setattr(faq_mod, "_DOC_EMB", doc_emb, raising=False)
    monkeypatch.setattr(faq_mod, "_EMBEDDER", FakeEmbedder(), raising=False)

    transport = ASGITransport(app=app)  # NEW

    async with LifespanManager(app):
        async with AsyncClient(transport=transport, base_url="http://test") as ac:  # CHANGED
            res = await ac.post("/faq/ask", json={"question": "demo booking please"})

    assert res.status_code == 200
    data = res.json()
    assert data["answer"] == "Use /bookings."
    assert data["source_id"] == "faq-001"
    assert 0.0 <= data["score"] <= 1.0
