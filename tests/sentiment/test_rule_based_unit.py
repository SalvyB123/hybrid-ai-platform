from __future__ import annotations

import math

import pytest

from src.ai.sentiment import classify


@pytest.mark.parametrize(
    "text,expected",
    [
        ("This tool is fantastic and helpful!", "positive"),
        ("Awful experience, totally clunky.", "negative"),
        ("It's okay, nothing special.", "neutral"),
        ("No issues so far.", "positive"),
        ("Absolutely love the new dashboard!", "positive"),
        ("I can't recommend this after it failed twice.", "negative"),
    ],
)
def test_basic_polarity(text: str, expected: str) -> None:
    res = classify(text)
    assert res.label == expected


def test_negation_simple() -> None:
    # direct "not <positive>"
    res = classify("The support was not helpful.")
    assert res.label == "negative"


def test_negation_windowed_ellipsis() -> None:
    # "<positive> ... not" within a short window
    res = classify("Setup was quick… not.")
    assert res.label == "negative"


def test_concession_but_neutralises() -> None:
    # mixed sentence with concession should land near neutral
    res = classify("Works, but I had to retry twice.")
    assert res.label == "neutral"


def test_hedges_pull_to_neutral() -> None:
    res = classify("The response was fine.")
    assert res.label == "neutral"


def test_case_insensitivity_and_whitespace() -> None:
    res = classify("  GREAT   value  once you get past the clunky onboarding ")
    # positive + negative -> hedge/concession dampening; expect positive or neutral.
    assert res.label in {"positive", "neutral"}


def test_empty_and_spaces_are_neutral() -> None:
    for txt in ["", "   ", "\n\t"]:
        res = classify(txt)
        assert res.label == "neutral"
        assert math.isfinite(res.score)


def test_determinism_multiple_runs() -> None:
    text = "Support was helpful, great value."
    results = [classify(text).label for _ in range(20)]
    # no randomness: all labels identical
    assert len(set(results)) == 1
