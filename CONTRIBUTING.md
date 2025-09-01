## Naming Conventions & Branch Strategy

### Git Commands

-   Prefer **modern Git** commands:
    -   Branches: `git switch` (create new: `git switch -c <name>`)
    -   Restore files: `git restore <path>`
-   Legacy equivalents (e.g. `git checkout`) still work, but are not used in new docs.

### Branches

-   **main**: always deployable; protect with required PR review + passing CI.
-   **Feature**: `feature/<scope>-<short-desc>`  
    Create with: `git switch -c feature/faq-thresholds`
-   **Fix**: `fix/<area>-<short-desc>`  
    Create with: `git switch -c fix/api-health-timeout`
-   **Chore**: `chore/<short-desc>`  
    Create with: `git switch -c chore/add-ruff`
-   **Docs**: `docs/<short-desc>`  
    Create with: `git switch -c docs/adr-forecasting`
-   **Hotfix**: `hotfix/<short-desc>` (urgent patch on `main`)
    Create with: `git switch -c hotfix/faq-bug`
-   **Release tags**: `v0.1.0` (SemVer)

### Pull Requests

-   **Title** uses Conventional Commits (see below).
-   Link issues with `Closes #<number>`.
-   Must pass CI; at least one review (for solo dev, self-review checklist in PR).
-   Uses `git switch` (not `git checkout -b`) in any shell snippets.

### Commit Messages (Conventional Commits)

**Format:** `type(scope): short summary`

**Types:** `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `build`, `ci`

**Examples**

-   `feat(faq): add confidence threshold + human handoff`
-   `fix(api): return 200 from /health in debug`
-   `chore(ci): add pytest step`

### Files & Folders

-   **Python packages/modules:** `snake_case` (e.g., `src/api/app.py`, `src/ai/faq/`)
-   **Classes:** `PascalCase`  
    **Functions/vars:** `snake_case`  
    **Constants:** `UPPER_SNAKE`
-   **Docs filenames:** `kebab-case.md` (e.g., `vertical-config-guide.md`)
-   **ADR files:** `adr/NNN-title.md` (3-digit index, e.g., `adr/002-database-choice.md`)
-   **DB migrations:** `YYYYMMDDHHMM_<desc>.py` (e.g., `20250816_0930_create_booking_tables.py`)

### Environment & Config

-   Env vars prefixed with `APP_` and `UPPER_SNAKE` (e.g., `APP_ENV`, `APP_DB_URL`).
-   Do **not** commit secrets. Use `.env` locally and GitHub Encrypted Secrets in CI.
-   Centralize config in `src/config/` with safe local defaults.

### Testing

-   Unit tests in `tests/unit/`, integration tests in `tests/integration/`.
-   Test files mirror module paths: `test_<module>.py`.

### Versioning

-   **Semantic Versioning:** `MAJOR.MINOR.PATCH`
-   Tag releases:
    ```bash
    git tag v0.1.0
    git push --tags
    ```
