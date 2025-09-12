# ADR-007: Sentiment Analysis Approach

## Status

Accepted — 2025-09-12

## Context

We need a free, deterministic Sentiment Dashboard V1 that runs locally on a MacBook Pro (M4, 24GB RAM) and integrates with our FastAPI backend. The goal is to label short user feedback as Positive / Negative / Neutral, store results in Postgres, and expose them via API for a simple chart. Costs must be £0 for inference.

We evaluated:

1. Rule-based polarity scoring (tiny lexicon + neutral band).
2. Lightweight Hugging Face model (distilbert-base-uncased-finetuned-sst-2-english) with an added neutral band.

## Decision

Adopt a **rule-based classifier** for V1.

**Evidence (devset=12):**

-   Rule-based: Accuracy **0.67** (8/12), Neutral rate **0.25**, ~**0 ms/sample**.
-   With minor lexicon/neutral-band tuning we expect **≥0.75** while staying deterministic and offline.
-   HF model is free but requires a ~250MB download and adds non-zero latency; sst-2 lacks explicit neutral.

## Consequences

-   **Pros:** Zero cost, instant inference, deterministic runs in CI, tiny footprint. Easy to reason about and adjust for our domain.
-   **Cons:** Limited linguistic coverage (sarcasm, complex negation, domain drift). Quality depends on lexicon tuning.
-   **Mitigations:** Keep a feature-flagged HF path for V2; expand lexicon gradually; collect real feedback text to refine.

## Implementation Notes

-   Module: `src/ai/sentiment/rule_based.py`
-   Endpoint: `POST /sentiment` returns `{text, score, label}` and persists to Postgres.
-   Testing: `tests/sentiment/test_devset_eval.py` enforces a baseline accuracy over the devset.
-   Future: Add optional HF path guarded by an environment flag for V2.

## References

-   ADRs: https://adr.github.io/
-   SST-2 task background (neutral gap acknowledged)
