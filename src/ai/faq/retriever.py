# src/ai/faq/retriever.py
from __future__ import annotations

import numpy as np


def cosine_top1(q_vec: np.ndarray, doc_mat: np.ndarray) -> tuple[int, float]:
    """
    Return (index, cosine) where cosine is in [-1, 1].
    Assumes q_vec and each row of doc_mat are L2-normalised.
    """
    sims = doc_mat @ q_vec  # (n,)
    idx = int(np.argmax(sims))
    return idx, float(sims[idx])


def score_from_cosine(cosine: float) -> float:
    """
    Map cosine in [-1, 1] to a user-facing score in [0, 1].
    """
    # Clamp then rescale
    c = max(-1.0, min(1.0, float(cosine)))
    return (c + 1.0) / 2.0
