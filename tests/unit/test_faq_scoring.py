from src.ai.faq.retriever import score_from_cosine


def test_score_from_cosine_bounds():
    assert score_from_cosine(-1.0) == 0.0
    assert score_from_cosine(1.0) == 1.0


def test_score_from_cosine_midpoint():
    assert score_from_cosine(0.0) == 0.5
