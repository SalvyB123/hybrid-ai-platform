from __future__ import annotations

import math


def clamp01(x: float) -> float:
    if math.isnan(x):
        return 0.0
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x


def should_handoff(score: float, threshold: float) -> bool:
    """
    Decide whether to hand off to a human based on score and threshold.
    - Inputs are clamped to [0,1] so misconfiguration can't break behaviour.
    - Handoff occurs only when score < threshold (strictly below).
    """
    s = clamp01(score)
    t = clamp01(threshold)
    return s < t
