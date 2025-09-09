from __future__ import annotations

from fastapi import APIRouter
import numpy as np

from src.ai.faq.data_loader import load_faqs
from src.ai.faq.embedder import load_or_build_embeddings, MiniLMEmbedder
from src.ai.faq.retriever import cosine_top1, score_from_cosine
from src.api.schemas.faq import FAQAskRequest, FAQAnswer, FAQHandoff
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
    if score < settings.faq_confidence_threshold:
        # Below confidence -> return handoff signal for next step (SMTP)
        return FAQHandoff(handoff=True, score=score, question=req.question)

    # Confident -> return curated answer
    item = _FAQS[idx]  # type: ignore[index]
    return FAQAnswer(answer=item.answer, score=score, source_id=item.id)
