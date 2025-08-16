# Hybrid AI Platform (Foundations)

An enterprise-ready, multi-vertical AI assistant platform. This repository starts with the **Foundations (Months 1–2)** phase and grows into the full plan.

## Why this structure?
- **Simple for a solo builder** now, but **scales** to multiple services later.
- Keeps AI, API, config, logging, and tests **modular**.
- **Docs + ADRs** show your decision-making to recruiters and future collaborators.

## Directory map
```
.github/workflows/      # CI setup (lint/test)
adr/                    # Architecture Decision Records
docs/                   # Diagrams, notes, planning
scripts/                # Dev and CI helper scripts
src/
  api/                  # FastAPI app (REST endpoints)
  ai/
    rag/                # Retrieval-Augmented Generation utilities
    faq/                # FAQ bot logic (RAG + thresholds + handoff)
    forecasting/        # Prophet baseline + interfaces
    sentiment/          # Sentiment analysis + action hooks
  clients/              # Integrations (e.g., Google Calendar)
  config/               # App settings, env parsing
  db/
    migrations/         # Database migrations
  logging/              # GDPR-safe logging utils
tests/
  unit/                 # Fast tests for functions/modules
  integration/          # Slower tests across components
```

## Getting started (later steps)
- Create and activate a virtual env (e.g., `python -m venv .venv`).
- Install dependencies (we'll add a `pyproject.toml` later).
- Run lint and tests via `make` (see `Makefile`).

## Roadmap references
See `/docs/roadmap.md` (placeholder) and ADRs in `/adr` for decisions.