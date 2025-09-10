from __future__ import annotations

import numpy as np
from fastapi import APIRouter

from src.ai.faq.data_loader import load_faqs
from src.ai.faq.decision import should_handoff
from src.ai.faq.embedder import MiniLMEmbedder, load_or_build_embeddings
from src.ai.faq.notify import FAQContext, send_handoff_email
from src.ai.faq.retriever import cosine_top1, score_from_cosine
from src.api.schemas.faq import FAQAnswer, FAQAskRequest, FAQHandoff
from src.config.settings import get_settings

router = APIRouter(prefix="/faq", tags=["faq"])
settings = get_settings()

# --- Lazy-initialised state (safe for tests) ---
_FAQS: list | None = None
_DOC_EMB: np.ndarray | None = None
_EMBEDDER: MiniLMEmbedder | None = None


@router.on_event("startup")
async def _warm_faq_state() -> None:
    global _FAQS, _DOC_EMB, _EMBEDDER
    # Only initialise if not already set (helps tests that monkeypatch state)
    if _FAQS is None or _DOC_EMB is None:
        _FAQS = load_faqs()
        qs = [f.question for f in _FAQS]
        _DOC_EMB, used_cache = load_or_build_embeddings(qs)
        _EMBEDDER = None if used_cache else MiniLMEmbedder()


@router.post(
    "/ask",
    response_model=FAQAnswer | FAQHandoff,  # can return either shape
)
async def ask(req: FAQAskRequest):
    # init-on-first-call fallback (for tests that don’t run startup)
    global _FAQS, _DOC_EMB, _EMBEDDER
    if _FAQS is None or _DOC_EMB is None:
        await _warm_faq_state()  # type: ignore[misc]

    if _EMBEDDER is None:
        q_emb = MiniLMEmbedder().encode([req.question])[0]
    else:
        q_emb = _EMBEDDER.encode([req.question])[0]

    idx, cosine = cosine_top1(q_emb, _DOC_EMB)  # type: ignore[arg-type]
    score = score_from_cosine(cosine)

    # Threshold check
    if should_handoff(score, settings.faq_confidence_threshold):  # CHANGED
        item = _FAQS[idx]  # type: ignore[index]
        ctx = FAQContext(id=item.id, question=item.question, answer=item.answer)
        _ = send_handoff_email(
            settings=settings,
            user_question=req.question,
            top_faq=ctx,
            score=score,
            threshold=settings.faq_confidence_threshold,
        )
        return FAQHandoff(handoff=True, score=score, question=req.question)

    # Confident -> return curated answer
    item = _FAQS[idx]  # type: ignore[index]
    return FAQAnswer(answer=item.answer, score=score, source_id=item.id)
