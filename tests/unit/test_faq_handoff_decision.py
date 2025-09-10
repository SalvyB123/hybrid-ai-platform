import pytest

from src.ai.faq.decision import clamp01, should_handoff


@pytest.mark.parametrize(
    "x, expected",
    [
        (-1.0, 0.0),
        (0.0, 0.0),
        (0.5, 0.5),
        (1.0, 1.0),
        (2.0, 1.0),
    ],
)
def test_clamp01_bounds_and_mid(x, expected):
    assert clamp01(x) == expected


def test_clamp01_nan_returns_zero():
    assert clamp01(float("nan")) == 0.0


@pytest.mark.parametrize(
    "score, thr, handoff",
    [
        # canonical cases
        (0.59, 0.60, True),
        (0.60, 0.60, False),  # equal -> no handoff
        (0.90, 0.60, False),
        # misconfiguration (clamped)
        (-0.1, 0.6, True),  # score -> 0.0 < 0.6
        (0.5, 1.5, True),  # thr -> 1.0 ; 0.5 < 1.0
        (1.2, 0.6, False),  # score -> 1.0
        (0.5, -0.2, False),  # thr -> 0.0
    ],
)
def test_should_handoff_logic(score, thr, handoff):
    assert should_handoff(score, thr) is handoff


def test_should_handoff_with_nan_inputs():
    # score=NaN -> 0.0; thr=0.6 -> handoff
    assert should_handoff(float("nan"), 0.6) is True
    # thr=NaN -> 0.0; score=0.5 -> no handoff
    assert should_handoff(0.5, float("nan")) is False
