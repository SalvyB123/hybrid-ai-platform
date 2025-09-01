# ADR 002: Database Choice & Migrations

-   Status: Accepted
-   Date: 2025-09-01
-   Decision: PostgreSQL 16 (Docker) + SQLAlchemy 2.0 (async) + Alembic

## Context

The platform needs a relational database to support multiple verticals. It must be enterprise-credible, scalable, and reproducible in CI/CD pipelines. We also need versioned schema management to evolve safely as features grow.

## Options Considered

-   **SQLite:** Lightweight, simple, but lacks concurrency and enterprise credibility.
-   **MySQL/MariaDB:** Viable, but weaker ecosystem for Python/AI workloads.
-   **PostgreSQL:** Mature, feature-rich (JSONB, CTEs, extensions), widely adopted in Python.
-   **Raw SQL migrations:** Manual, error-prone, hard to manage across environments.
-   **Alembic:** Standard Python migration tool, integrates with SQLAlchemy metadata, works in CI/CD.

## Decision

-   **Primary DB:** PostgreSQL 16
-   **Local runtime:** Dockerised Postgres with persistent volume
-   **Driver/ORM:** SQLAlchemy 2.0 (async) with asyncpg
-   **Migrations:** Alembic, tracked in `migrations/`
-   **Secrets:** `.env` locally, GitHub Actions Secrets in CI

## Rationale

-   **Technical:** Strong typing, transactions, JSONB, extensions. Alembic gives reproducible, reversible schema changes.
-   **Strategic:** Aligns with enterprise standards and recruiter expectations.
-   **Cost:** Local Docker is free; cloud Postgres (Neon/Supabase/RDS) have generous free tiers.
-   **Future-proofing:** Smooth path to managed Postgres in later milestones.

## Consequences

-   Slightly more setup complexity (Docker + Alembic).
-   Developers must follow migration discipline.
-   Provides a professional baseline for later cloud deployments.

## Links

-   `docker-compose.yml`
-   `.env.example`
-   `src/config/settings.py`
-   `src/db/session.py`
-   `migrations/`
