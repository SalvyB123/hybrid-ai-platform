import numpy as np
from src.ai.faq.retriever import cosine_top1


def test_cosine_top1_selects_highest():
    # Two orthogonal docs; query matches the first doc exactly.
    docs = np.array([[1.0, 0.0], [0.0, 1.0]], dtype="float32")
    q = np.array([1.0, 0.0], dtype="float32")
    idx, score = cosine_top1(q, docs)
    assert idx == 0
    assert score == 1.0
