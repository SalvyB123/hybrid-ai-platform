# ADR 004: Python Tooling (venv+pip, ruff/black, pytest)

Date: 2025-08-16  
Status: Proposed

## Context

We need simple, low-friction Python tooling suitable for a solo developer that remains professional and scalable. Key needs: easy environment setup, reliable formatting/linting, and a standard test runner. Costs should be zero for now.

## Decision

Use `venv + pip` for environments and dependency management, `requirements.txt` and `requirements-dev.txt` for clarity, `black` for formatting, `ruff` for linting, and `pytest` for tests. Add optional VS Code settings to enable format-on-save.

## Options Considered

-   **venv + pip (Chosen)**:
    -   Pros: Simple, built-in, no extra concepts; plays well with GitHub Actions.
    -   Cons: Fewer features than Poetry (no lock file by default).
-   **Poetry**:
    -   Pros: Nice dependency resolution and lockfile; scripts.
    -   Cons: Extra learning/commands; overkill for current scope.
-   **Pre-commit hooks**:
    -   Pros: Enforce style locally before commits.
    -   Cons: Slight onboarding friction; can add later.

## Consequences

-   Fast onboarding and minimal friction for MVP.
-   Clear separation of runtime vs dev dependencies.
-   CI enforces style and tests via ruff/black/pytest.

## Follow-ups

-   Consider `pre-commit` once the codebase grows.
-   Revisit Poetry if multi-package layout emerges or dependency complexity increases.
