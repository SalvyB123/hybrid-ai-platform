import types

import numpy as np
import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from src.api.app import app


@pytest.mark.asyncio
async def test_faq_ask_validation_errors_on_empty_question():
    transport = ASGITransport(app=app)
    async with LifespanManager(app):
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            # Empty/invalid payload should fail validation (422)
            res = await ac.post("/faq/ask", json={"question": ""})
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_faq_ask_above_threshold_returns_answer(monkeypatch):
    """
    Endpoint should return a proper FAQAnswer when score >= threshold.
    No network or model downloads — everything monkeypatched.
    """
    import src.api.routes.faq as faq_mod

    class FakeEmbedder:
        def encode(self, texts):
            # Query → [1, 0]
            return np.vstack([np.array([1.0, 0.0], dtype="float32") for _ in texts])

    # Perfect match to ensure score = 1.0 (>= threshold)
    faqs = [types.SimpleNamespace(id="faq-001", question="Book a demo?", answer="Use /bookings.")]
    doc_emb = np.array([[1.0, 0.0]], dtype="float32")

    monkeypatch.setattr(faq_mod, "_FAQS", faqs, raising=False)
    monkeypatch.setattr(faq_mod, "_DOC_EMB", doc_emb, raising=False)
    monkeypatch.setattr(faq_mod, "_EMBEDDER", FakeEmbedder(), raising=False)
    monkeypatch.setattr(faq_mod.settings, "faq_confidence_threshold", 0.20, raising=False)

    # Defensive: ensure we don't accidentally send email on this path
    calls = {"n": 0}

    def never_called(*args, **kwargs):
        calls["n"] += 1
        return True

    monkeypatch.setattr(faq_mod, "send_handoff_email", never_called, raising=False)

    transport = ASGITransport(app=app)
    async with LifespanManager(app):
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            res = await ac.post("/faq/ask", json={"question": "demo please"})

    assert res.status_code == 200
    data = res.json()
    # Answer shape (not a handoff)
    assert "answer" in data and "source_id" in data and "score" in data
    assert "handoff" not in data
    assert data["answer"] == "Use /bookings."
    assert data["source_id"] == "faq-001"
    assert 0.0 <= data["score"] <= 1.0
    # Confirm email helper was not called
    assert calls["n"] == 0
