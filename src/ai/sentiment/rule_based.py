from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass

# Phrase/word lexicons (expand gradually as we see real data)
POS = {
    "fantastic",
    "helpful",
    "quick",
    "love",
    "great",
    "great value",
    "no issues",
    "works well",
    "support was helpful",
}

# Keep "retry" out of NEG (we'll treat it as a neutral hint below)
NEG = {
    "awful",
    "looping",
    "failed",
    "clunky",
    "can't recommend",
    "cant recommend",
    # "faster" kept as a weak negative cue via NEUTRAL_HINTS when phrased as disappointment
}

# Hedges / neutral cues that should pull overall sentiment toward neutral
NEUTRAL_HINTS = {
    "okay",
    "fine",
    "nothing special",
    "works",
    "retry",  # over-penalising this makes mixed sentences too negative
    "had to retry",
    "but",  # presence of concession often implies mixed sentiment
    "i thought it would be",  # expectation-hedging
}


@dataclass
class SentimentResult:
    score: float
    label: str  # "positive" | "negative" | "neutral"


def _normalise(text: str) -> str:
    # lower + collapse whitespace
    return " ".join(text.lower().split())


def _count_hits(text: str, phrases: Iterable[str]) -> int:
    return sum(1 for w in phrases if w in text)


def _tokenise(text: str) -> list[str]:
    # simple tokens for proximity rules; keep words only
    return re.findall(r"[a-z']+", text.lower())


def _windowed_negation(text: str, pos_phrases: Iterable[str], window: int = 4) -> int:
    """
    Count positive phrases that are negated by a nearby 'not' (or trailing ... not).
    Matches cases like:
      - "not helpful", "not great"
      - "setup was quick ... not"
    Returns the number of flips to apply (each flip = subtract one pos_weight).
    """
    t = _normalise(text)
    tokens = _tokenise(text)

    flips = 0

    # Pattern A: "not <positive>"
    for w in pos_phrases:
        if f"not {w}" in t:
            flips += 1

    # Pattern B: "<positive> ... not" (within window tokens)
    # find last occurrence of "not" and see if a POS phrase
    # appears within the previous window tokens
    try:
        last_not_idx = max(i for i, tok in enumerate(tokens) if tok == "not")
    except ValueError:
        last_not_idx = -1

    if last_not_idx != -1:
        window_start = max(0, last_not_idx - window)
        window_tokens = " ".join(tokens[window_start:last_not_idx])
        for w in pos_phrases:
            if w in window_tokens:
                flips += 1
                break

    return flips


def classify(
    text: str,
    pos_weight: float = 1.0,
    neg_weight: float = 1.0,
    neutral_band: float = 0.15,
) -> SentimentResult:
    """
    Deterministic, tiny rule-based classifier with:
      - phrase-first scoring
      - windowed negation handling ("not helpful", "quick ... not")
      - concession / hedge dampening ("works, but ...", "okay", "nothing special")
      - neutral band clamp
    """
    t = _normalise(text)
    score = 0.0

    # Phrase-first scoring
    pos_hits = _count_hits(t, POS)
    neg_hits = _count_hits(t, NEG)
    score += pos_weight * pos_hits
    score -= neg_weight * neg_hits

    # Windowed negation flips: each flip reverses one positive weight
    flips = _windowed_negation(text, POS, window=4)
    if flips:
        score -= pos_weight * flips  # invert previously added positive weights

    # Concession / hedge dampening
    hedges = _count_hits(t, NEUTRAL_HINTS)
    if " but " in f" {t} " or ", but" in t or "… but" in t:
        hedges += 1
    if hedges:
        # Pull toward neutral without fully zeroing meaningful sentiment
        score *= 0.6

    # If both sides fire, favour neutrality when magnitudes are close
    if pos_hits and neg_hits and abs(score) <= (pos_weight + neg_weight) * 0.6:
        score *= 0.7

    # Neutral clamp
    label = "neutral"
    if score > neutral_band:
        label = "positive"
    elif score < -neutral_band:
        label = "negative"

    return SentimentResult(score=score, label=label)
