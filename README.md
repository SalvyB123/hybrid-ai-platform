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

---

## Prerequisites

-   **Python** 3.11.x
-   **Node.js** ≥ 20, **npm** ≥ 9
-   **PostgreSQL** 16 (local Docker or service)
-   **Make** (optional, for convenience)

---

## Environment

Create a `.env` at the repository root (used by the backend and CI):

```env
# Database
APP_DB_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/app

# CORS (JSON array, parsed by pydantic-settings)
CORS_ALLOWED_ORIGINS=["http://localhost:5173"]

# Optional: logging level, etc.
LOG_LEVEL=INFO
```

CI uses the same shape (see .github/workflows/ci.yml).

---

## Backend (FastAPI) - Setup and Run

Create and activate a virtual environment, then install:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip

# Install app + dev deps
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

Run **migrations:**

```bash
# Ensure Postgres is running and APP_DB_URL points to it
python -m alembic upgrade head
```

Start the API:

```bash
uvicorn src.api.app:app --reload
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

Health & readiness:

```bash
curl -sf http://localhost:8000/health
curl -sf http://localhost:8000/readiness
```

---

## Frontend (Vite + React + Tailwind) – Setup & Run

From the `frontend/` directory:

```bash
cd frontend
npm ci
npm run dev
# App: http://localhost:5173
```

The frontend expects the API at http://localhost:8000. You can override via:

```bash
# frontend/.env.local
VITE_API_BASE_URL=http://localhost:8000
```

---

## Sentiment API – Usage

**1) Analyse sentiment (persisted)**

```bash
curl -X POST http://localhost:8000/sentiment \
  -H "Content-Type: application/json" \
  -d '{"text":"Support was helpful and great value."}'
```

**Response (201):**

```json
{
    "id": "a2c2ce2d-2f9b-4d6d-94e2-6e8c1c3aa001",
    "text": "Support was helpful and great value.",
    "score": 0.74,
    "label": "positive"
}
```

Validation & errors:

-   Empty text → 422 with error message
-   Excessively long text → 422
-   DB failure → 500 with a standard error envelope

**2) Summarise sentiment (for dashboard)**

```bash
curl -s http://localhost:8000/sentiment/summary | jq
```

**Response (200):**

```json
{
    "positive": 12,
    "negative": 3,
    "neutral": 4,
    "total": 19
}
```

The **frontend dashboard** consumes `/sentiment/summary` to render totals and a Positive vs Negative bar chart.

---

## Frontend Dashboard - What to Expect

-   Navigate to http://localhost:5173/login, sign in (stub) → redirected to /dashboard.
-   Dashboard shows:
    -   Summary cards: Total, Positive, Negative
    -   Bar chart (Recharts)
    -   Loading spinner and graceful error state

**Screenshot:**
To be added

---

### Running Tests

**Backend (pytest):**

```bash
source .venv/bin/activate
pytest -q
```

**Frontend (Vitest + Cypress):**

```bash
cd frontend
npm run test        # unit
npm run cy:run      # e2e (starts Vite and runs Cypress)
```

---

### Lint & Format

**Python (Ruff + Black):**

```bash
ruff check . --fix
black --check .
```

**JS/TS (ESLint + Prettier):**

```bash
cd frontend
npm run lint
npm run format:check
```

Pre-commit hooks can run these automatically on commit; see .pre-commit-config.yaml (Python) and Husky + lint-staged (frontend).

---

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

**Where things live:**

-   Migration scripts: src/db/migrations/versions/
-   Alembic config: alembic.ini, src/db/migrations/env.py
-   SQLAlchemy Base: src/db/session.py

---

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

---

### CI/CD

Our GitHub Actions workflow (.github/workflows/ci.yml) runs:

```bash
python -m alembic upgrade head
```

before executing tests to ensure the schema is always up to date.

---

### Roadmap references

See `/docs/roadmap.md` (placeholder) and ADRs in `/adr` for decisions.# trigger ci

---

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
