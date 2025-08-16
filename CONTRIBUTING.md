## Naming Conventions & Branch Strategy

### Branches
- **main**: always deployable; protect with required PR review + passing CI.
- **Feature**: `feature/<scope>-<short-desc>`  
  e.g. `feature/faq-thresholds`, `feature/booking-db`
- **Fix**: `fix/<area>-<short-desc>`  
  e.g. `fix/api-health-timeout`
- **Chore**: `chore/<short-desc>`  
  e.g. `chore/add-ruff`
- **Docs**: `docs/<short-desc>`  
  e.g. `docs/adr-forecasting`
- **Hotfix**: `hotfix/<short-desc>` (urgent patch on `main`)
- **Release tags**: `v0.1.0` (SemVer)

### Pull Requests
- **Title** uses Conventional Commits (see below).
- Link issues with `Closes #<number>`.
- Must pass CI; at least one review (for solo dev, self-review checklist in PR).

### Commit Messages (Conventional Commits)
**Format:** `type(scope): short summary`

**Types:** `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `build`, `ci`

**Examples**
- `feat(faq): add confidence threshold + human handoff`
- `fix(api): return 200 from /health in debug`
- `chore(ci): add pytest step`

### Files & Folders
- **Python packages/modules:** `snake_case` (e.g., `src/api/app.py`, `src/ai/faq/`)
- **Classes:** `PascalCase`  
  **Functions/vars:** `snake_case`  
  **Constants:** `UPPER_SNAKE`
- **Docs filenames:** `kebab-case.md` (e.g., `vertical-config-guide.md`)
- **ADR files:** `adr/NNN-title.md` (3-digit index, e.g., `adr/002-database-choice.md`)
- **DB migrations:** `YYYYMMDDHHMM_<desc>.py` (e.g., `20250816_0930_create_booking_tables.py`)

### Environment & Config
- Env vars prefixed with `APP_` and `UPPER_SNAKE` (e.g., `APP_ENV`, `APP_DB_URL`).
- Do **not** commit secrets. Use `.env` locally and GitHub Encrypted Secrets in CI.
- Centralize config in `src/config/` with safe local defaults.

### Testing
- Unit tests in `tests/unit/`, integration tests in `tests/integration/`.
- Test files mirror module paths: `test_<module>.py`.

### Versioning
- **Semantic Versioning:** `MAJOR.MINOR.PATCH`
- Tag releases:  
  ```bash
  git tag v0.1.0
  git push --tags
