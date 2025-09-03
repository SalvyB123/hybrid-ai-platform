# ADR-005: Schema Migrations with Alembic

Date: 2025-09-03  
Status: Accepted

## Context

The platform requires a way to manage database schema changes over time. As new features (Bookings, Sentiment, Forecasting, etc.) are added, we need a consistent, version-controlled method to evolve the schema across developer machines, CI pipelines, and production-like environments.

Constraints:

-   Must integrate with SQLAlchemy 2.0 in async mode.
-   Must be lightweight and cost-free for the MVP phase.
-   Must demonstrate enterprise credibility and reproducibility to recruiters.

## Decision

Adopt Alembic, configured in async mode, with migrations stored under `src/db/migrations` and metadata sourced from `src/db/session.Base`. A baseline migration will be created to anchor schema history, and CI will run `alembic upgrade head` before tests to ensure consistency.

## Options Considered

-   **Manual SQL scripts**

    -   Pros: Simple, no external dependency.
    -   Cons: Error-prone, no versioning, difficult to reproduce in CI/CD.

-   **SQLAlchemy `create_all()` at runtime**

    -   Pros: Minimal setup effort.
    -   Cons: Not enterprise-grade; no audit trail of schema changes; no rollback capability.

-   **Alembic (Chosen)**
    -   Pros: Standard tool with SQLAlchemy; provides versioned migrations, reproducibility, and rollback capability; integrates with async engine.
    -   Cons: Slight learning curve; requires maintaining migration files.

## Consequences

Positive outcomes:

-   Provides versioned, auditable schema changes.
-   Ensures consistent environments across dev and CI.
-   Establishes enterprise credibility in repo history.

Risks and mitigations:

-   Risk: Incorrect autogeneration diffs. Mitigation: manual review of migrations before committing.
-   Risk: Added workflow complexity. Mitigation: Makefile shortcuts for common commands.

Follow-up tasks:

-   Add Makefile helpers (`mig-rev`, `mig-up`, `mig-down`).
-   Update CI to run `alembic upgrade head` before tests.
-   Document migration workflow in README.

## Links

-   Related ADRs: ADR-002 (Database Choice), ADR-004 (Python Tooling)
-   Issues / PRs: `feat/alembic-baseline` branch, Week 3 sprint tasks
-   Docs: [Alembic Documentation](https://alembic.sqlalchemy.org/)
