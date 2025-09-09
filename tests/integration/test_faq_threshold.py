import types
import numpy as np
import pytest
from httpx import AsyncClient, ASGITransport
from asgi_lifespan import LifespanManager
from src.api.app import app


@pytest.mark.asyncio
async def test_faq_ask_below_threshold_triggers_handoff(monkeypatch):
    import src.api.routes.faq as faq_mod

    # Fake embedder: query vector is [1,0]
    class FakeEmbedder:
        def encode(self, texts):
            return np.vstack([np.array([1.0, 0.0], dtype="float32") for _ in texts])

    # One document with cosine=0.6 against query -> score=(0.6+1)/2=0.8
    faqs = [
        types.SimpleNamespace(id="faq-low", question="Low-sim question", answer="Low-sim answer")
    ]
    doc_emb = np.array([[0.6, 0.8]], dtype="float32")  # unit length

    # Patch runtime state and raise the threshold to 0.95 to force handoff
    monkeypatch.setattr(faq_mod, "_FAQS", faqs, raising=False)
    monkeypatch.setattr(faq_mod, "_DOC_EMB", doc_emb, raising=False)
    monkeypatch.setattr(faq_mod, "_EMBEDDER", FakeEmbedder(), raising=False)
    monkeypatch.setattr(faq_mod.settings, "faq_confidence_threshold", 0.95, raising=False)

    transport = ASGITransport(app=app)
    async with LifespanManager(app):
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            res = await ac.post("/faq/ask", json={"question": "will this hand off?"})

    assert res.status_code == 200
    data = res.json()
    # Handoff payload expected
    assert data.get("handoff") is True
    assert "question" in data and "score" in data
    # No 'answer' or 'source_id' in handoff response
    assert "answer" not in data and "source_id" not in data
