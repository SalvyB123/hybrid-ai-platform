from __future__ import annotations
import numpy as np


def cosine_top1(q_vec: np.ndarray, doc_mat: np.ndarray) -> tuple[int, float]:
    """Return index and similarity (0..1). Assumes vectors are L2-normalised."""
    sims = doc_mat @ q_vec  # (n,)
    idx = int(np.argmax(sims))
    return idx, float(sims[idx])
