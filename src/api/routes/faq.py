from __future__ import annotations
from fastapi import APIRouter

from src.ai.faq.data_loader import load_faqs
from src.ai.faq.embedder import load_or_build_embeddings, MiniLMEmbedder
from src.ai.faq.retriever import cosine_top1
from src.api.schemas.faq import FAQAskRequest, FAQAnswer

router = APIRouter(prefix="/faq", tags=["faq"])

# --- Warm state (module-level for simplicity) ---
_FAQS = load_faqs()
_QS = [f.question for f in _FAQS]
_DOC_EMB, _USED_CACHE = load_or_build_embeddings(_QS)
_EMBEDDER = None if _USED_CACHE else MiniLMEmbedder()


@router.post("/ask", response_model=FAQAnswer)
async def ask(req: FAQAskRequest) -> FAQAnswer:
    """Return top-1 FAQ answer with similarity score."""
    if _EMBEDDER is None:
        # If embeddings were loaded from cache, we still need an encoder for the query.
        q_emb = MiniLMEmbedder().encode([req.question])[0]
    else:
        q_emb = _EMBEDDER.encode([req.question])[0]

    idx, score = cosine_top1(q_emb, _DOC_EMB)
    item = _FAQS[idx]
    return FAQAnswer(answer=item.answer, score=score, source_id=item.id)
