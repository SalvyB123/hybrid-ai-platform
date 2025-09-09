# Hybrid AI Platform (Foundations)

An enterprise-ready, multi-vertical AI assistant platform. This repository starts with the **Foundations (Months 1–2)** phase and grows into the full plan.

## Why this structure?

-   **Simple for a solo builder** now, but **scales** to multiple services later.
-   Keeps AI, API, config, logging, and tests **modular**.
-   **Docs + ADRs** show your decision-making to recruiters and future collaborators.

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

-   Create and activate a virtual env (e.g., `python -m venv .venv`).
-   Install dependencies (we'll add a `pyproject.toml` later).
-   Run lint and tests via `make` (see `Makefile`).

## Database Migrations (Alembic – Async)

We use [Alembic](https://alembic.sqlalchemy.org/) for schema migrations, configured for **SQLAlchemy 2.0 async**.

### Common commands

Generate a new migration from models:

```bash
make mig-rev m="add booking table"
```

Apply the latest migrations:

```bash
make mig-up
```

Roll back one step:

```bash
make mig-down s="-1"
```

View migration history:

```bash
make mig-history
```

Check the current migration:

```bash
make mig-current
```

### Where things live

-   Migration scripts: src/db/migrations/versions/
-   Alembic config: alembic.ini, src/db/migrations/env.py
-   SQLAlchemy Base: src/db/session.py

### CI/CD

Our GitHub Actions workflow (.github/workflows/ci.yml) runs:

```bash
python -m alembic upgrade head
```

before executing tests to ensure the schema is always up to date.

### Roadmap references

See `/docs/roadmap.md` (placeholder) and ADRs in `/adr` for decisions.# trigger ci

### FAQ BOT (V1)

The FAQ Bot is a minimal retrieval-based assistant. It loads a small set of curated FAQs `from data/faqs.yaml`, encodes them into embeddings, and serves answers through a FastAPI endpoint.
This approach keeps costs at zero (no paid APIs) and ensures deterministic behaviour. If a question is close enough to one of the stored FAQs, the corresponding answer is returned.

# Quickstart

1. Run the API:

```bash
uvicorn src.api.app:app --reload
```

2. Ask a question:

```bash
curl -X POST http://localhost:8000/faq/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"How do I book a demo?"}'
```

3. Expected respsone:

```bash
{
  "answer": "Create a booking via POST /bookings or email demo@example.local.",
  "score": 0.89,
  "source_id": "faq-001"
}
```

# How it works

-   **Data souce:** `data/faqs.yaml` stores questions and answers.
-   **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2` (downloaded on first run) encodes the questions.
-   **Retrieval:** Cosine similarity is used to find the closest match.
-   **API contract:** `POST /faq/ask` with a question returns the best-matched FAQ answer.
-   **Tests:** Unit and integration tests validate retrieval behaviour without requiring external services.

### Confidence and fallback

Each FAQ answer is returned with a **confidence score** between 0 and 1.  
This score is derived from cosine similarity and normalised by `(cosine + 1) / 2`.

-   If the score is **greater than or equal to** the configured threshold (`FAQ_CONFIDENCE_THRESHOLD`, default `0.60`), the FAQ Bot returns the curated answer and its source id.
-   If the score is **below** the threshold, the bot does **not** guess. Instead, it:
    1. Returns a `handoff` response in the API output.
    2. Triggers an **email notification** (via SMTP, e.g. MailHog in local dev) containing:
        - The user’s original question
        - The closest FAQ match (id, question, answer)
        - The score and threshold values

This design ensures graceful fallback: users aren’t misled by low-confidence answers, and humans stay in the loop for questions outside the curated set.

**Local email (MailHog):**

```bash
docker run -d --name mailhog -p 1025:1025 -p 8025:8025 mailhog/mailhog
open http://localhost:8025
```

## Branching & PRs (modern Git)

We use modern Git commands. Prefer `git switch` for branches and `git restore` for files.
Legacy `git checkout` is equivalent but not used in new docs.

# keep main up to date

git fetch origin
git switch main
git pull --ff-only

# start a task branch

git switch -c feature/<area>-<short-desc>

# commit using Conventional Commits

git add .
git commit -m "feat(<area>): <summary>"

# push and open a PR

git push -u origin feature/<area>-<short-desc>
