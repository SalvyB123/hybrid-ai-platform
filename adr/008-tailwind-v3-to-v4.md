# ADR-008 — Tailwind v3 now; planned upgrade to v4

-   **Status:** Accepted
-   **Date:** 2025-09-16
-   **Decision owners:** Platform team
-   **Context:** Frontend uses Tailwind CSS for utility-first styling and design tokens. Tailwind v4 introduces a new engine, config changes, and improved performance, but is early for some plugin ecosystems.

## Decision

Adopt **Tailwind v3** for the current sprint and near-term releases to ensure stability and predictable plugin support (e.g., `tailwindcss-animate`, shadcn/ui baselines). Plan a managed upgrade to **Tailwind v4** once our component library and CI are ready.

## Rationale

-   **Stability now:** v3 is mature and stable for recruiter demos and e2e tests.
-   **Ecosystem alignment:** shadcn/ui and our existing tokens are verified with v3.
-   **Risk reduction:** Avoid upgrade churn while building core features (Sentiment Dashboard V1, Cypress suite, ProtectedRoute).

## Options considered

1. **Upgrade to v4 immediately**

    - **Pros:** Smaller runtime, improved performance, modern config.
    - **Cons:** Plugin compatibility gaps; migration time; potential CI instability.

2. **Stay on v3 (chosen)**
    - **Pros:** Stable, known-good setup; zero disruption to delivery.
    - **Cons:** Defers performance gains and new features in v4.

## Migration plan to Tailwind v4 (when ready)

1. **Spike branch:** `chore/tailwind-v4-spike`
    - Upgrade deps: `tailwindcss@^4`, `postcss`, `autoprefixer` (as required by v4).
    - Replace legacy config with v4 style (v4 simplifies or removes `content`, `theme.extend` patterns).
2. **Tokens & utilities:**
    - Re-map design tokens from `tailwind.config.cjs` to v4 equivalents.
    - Verify `@apply` usage in global styles; update if syntax changed.
3. **Plugins & components:**
    - Test `tailwindcss-animate` / shadcn/ui with v4; remove/replace incompatible utilities.
    - Run `npm run build` and snapshot diffs for class changes.
4. **Tooling & CI:**
    - Ensure ESLint/Prettier formatting unaffected.
    - Run Cypress e2e against the spike; fix regressions.
5. **Rollout:**
    - Open PR with a concise migration guide and screenshots.
    - Gate merge on green CI (lint, typecheck, build, Cypress).

## Impact

-   **Short term:** No disruption; v3 remains the baseline.
-   **Medium term:** A single, planned upgrade window to v4 with a focused validation checklist.
-   **Risk:** Minor duplication of tokens during spike; mitigated by branch isolation and CI gates.

## References

-   Tailwind docs and migration guide (consult during spike).
-   Internal components and tokens (`frontend/tailwind.config.cjs`, `src/styles/globals.css`).
