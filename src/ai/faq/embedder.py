from __future__ import annotations

from pathlib import Path

import numpy as np

_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_EMB_CACHE = Path("data/faqs_embeddings.npy")


class MiniLMEmbedder:
    """Thin wrapper so we can swap models later without touching callers."""

    def __init__(self) -> None:
        from sentence_transformers import SentenceTransformer  # lazy import

        self.model = SentenceTransformer(_MODEL_NAME)

    def encode(self, texts: list[str]) -> np.ndarray:
        vecs = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,  # cosine-ready
        )
        return vecs.astype("float32")


def load_or_build_embeddings(questions: list[str]) -> tuple[np.ndarray, bool]:
    """Return (embeddings, used_cache)."""
    if _EMB_CACHE.exists():
        return np.load(_EMB_CACHE), True
    emb = MiniLMEmbedder().encode(questions)
    return emb, False
