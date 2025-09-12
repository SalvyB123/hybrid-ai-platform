# ADR-007: Sentiment Analysis Approach

## Status

Proposed  
(Date: YYYY-MM-DD)

## Context

We need a sentiment analysis pipeline for the **Sentiment Dashboard V1**.  
Constraints:

-   Must be **free/local** (no paid APIs).
-   Must be **deterministic** enough for demos.
-   Must be **lightweight** to run locally (MacBook Pro M4, 24GB RAM).
-   Goal: classify user feedback as Positive / Negative / Neutral and display results in a dashboard.

Options considered:

1. **Rule-based polarity scoring** (e.g., simple wordlist or VADER-like approach).
2. **Lightweight Hugging Face model** (pretrained transformer such as `distilbert-base-uncased-finetuned-sst-2-english`).

## Decision

(TBD after testing options)

## Consequences

(TBD – will explain trade-offs once decision is final)

## References

-   [ADR template reference](https://adr.github.io/)
-   Hugging Face sentiment model card (link)
-   VADER Sentiment docs (link)
