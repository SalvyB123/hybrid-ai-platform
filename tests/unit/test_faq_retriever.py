import math
import numpy as np
import pytest

from src.ai.faq.retriever import cosine_top1, score_from_cosine


def test_cosine_top1_perfect_match():
    # Two orthogonal docs; query equals doc 0
    docs = np.array([[1.0, 0.0], [0.0, 1.0]], dtype="float32")
    q = np.array([1.0, 0.0], dtype="float32")
    idx, cos = cosine_top1(q, docs)
    assert idx == 0
    assert cos == 1.0


def test_cosine_top1_selects_larger_similarity():
    # Doc0 has 0.8 similarity, Doc1 has 0.6 similarity
    d0 = np.array([0.8, 0.6], dtype="float32")  # L2 ≈ 1.0
    d1 = np.array([0.6, 0.8], dtype="float32")
    docs = np.vstack([d0 / np.linalg.norm(d0), d1 / np.linalg.norm(d1)])

    q = np.array([1.0, 0.0], dtype="float32")  # normalised
    q = q / np.linalg.norm(q)
    idx, cos = cosine_top1(q, docs)
    assert idx in (0, 1)  # not equal sims, but assert we get a valid index
    # Explicitly compute which is larger to assert deterministically
    sims = docs @ q
    assert cos == pytest.approx(float(np.max(sims)), rel=1e-6)
    assert idx == int(np.argmax(sims))


def test_cosine_top1_tie_breaker_returns_first_max_index():
    # Both docs identical -> same cosine; argmax should return first index
    d = np.array([1.0, 0.0], dtype="float32")
    docs = np.vstack([d, d])
    q = d
    idx, cos = cosine_top1(q, docs)
    assert idx == 0
    assert cos == 1.0


@pytest.mark.parametrize(
    "cosine, expected",
    [
        (-1.0, 0.0),
        (-0.5, 0.25),
        (0.0, 0.5),
        (0.5, 0.75),
        (1.0, 1.0),
        (2.0, 1.0),  # clamped
        (-2.0, 0.0),  # clamped
    ],
)
def test_score_from_cosine_mapping_and_clamp(cosine, expected):
    assert score_from_cosine(cosine) == pytest.approx(expected, rel=1e-6)


def test_cosine_top1_handles_many_docs_fast():
    # Sanity test for performance on small matrices
    rng = np.random.default_rng(42)
    docs = rng.normal(size=(1000, 16)).astype("float32")
    # L2 normalise rows
    docs /= np.linalg.norm(docs, axis=1, keepdims=True)
    q = rng.normal(size=(16,)).astype("float32")
    q /= np.linalg.norm(q)
    idx, cos = cosine_top1(q, docs)
    assert 0 <= idx < docs.shape[0]
    assert -1.0 <= cos <= 1.0
    assert not math.isnan(cos)
