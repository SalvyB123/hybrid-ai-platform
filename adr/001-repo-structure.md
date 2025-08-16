# ADR 001: Repository Structure and Monorepo Choice

Date: 2025-08-16
Status: Proposed

## Context
We need a structure that is beginner-friendly, supports Months 1–2 features (FAQ bot, forecasting, sentiment, booking), and scales to enterprise hooks later. We are a solo developer optimizing for clarity, low cost, and recruiter visibility.

## Decision
Use a **single repository** with a modular folder layout (`src/api`, `src/ai`, `src/config`, `src/db`, etc.). Keep room for future services without the overhead of a full monorepo toolchain.

## Options Considered
- **Single repo, modular folders (Chosen):**
  - Pros: Simple for one person, easy onboarding, minimal tooling, works well with GitHub Projects.
  - Cons: If it grows to many services, boundaries can blur.
- **Monorepo with multiple services (e.g., api, worker, frontend):**
  - Pros: Clear boundaries, independent deploys later.
  - Cons: More complex tooling (workspaces), higher cognitive load now.
- **Multiple repos (polyrepo):**
  - Pros: Strong isolation.
  - Cons: Overhead for a solo builder; cross-repo changes are harder.

## Consequences
- We can move fast now, while keeping clear directories for features.
- If the project grows, we can split services into packages or separate repos later.
- CI remains simple initially; we can shard jobs when needed.

## Follow-ups
- Add a `pyproject.toml` with tool configs (ruff/black/pytest).
- Create initial FastAPI boilerplate under `src/api`.
- Add Makefile and CI workflow to lint/test.