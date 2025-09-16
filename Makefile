.PHONY: help install lint test test-cov run format fix

help:
	@echo "Common commands:"
	@echo "  make install    - install runtime + dev dependencies"
	@echo "  make format     - run black (code formatter)"
	@echo "  make lint       - run ruff (linter)"
	@echo "  make fix        - auto-fix lint issues where possible"
	@echo "  make test       - run pytest"
	@echo "  make test-cov   - run pytest with coverage"
	@echo "  make run        - run local API (uvicorn)"

install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

format:
	black .

lint:
	ruff check .

fix:
	ruff check . --fix || true
	black .

test:
	pytest -q

test-cov:
	coverage run -m pytest -q
	coverage report -m

run:
	python -m uvicorn src.api.app:app --reload --port 8000

.PHONY: db-up db-down db-logs db-psql

db-up:
	docker compose up -d db

db-down:
	docker compose down

db-logs:
	docker compose logs -f db

db-psql:
	@set -a; [ -f .env ] && . .env; set +a; \
	docker compose exec -T db psql -U $$APP_DB_USER -d $$APP_DB_NAME -c "$(c)"

# --- Alembic helpers ---
ALEMBIC=python -m alembic

mig-rev:
	@if [ -z "$(m)" ]; then echo "Usage: make mig-rev m=\"message\""; exit 1; fi
	$(ALEMBIC) revision --autogenerate -m "$(m)"

mig-up:
	$(ALEMBIC) upgrade head

mig-down:
	@if [ -z "$(s)" ]; then echo "Usage: make mig-down s=\"-1\""; exit 1; fi
	$(ALEMBIC) downgrade $(s)

mig-history:
	$(ALEMBIC) history

mig-current:
	$(ALEMBIC) current

# --- Dev convenience targets (backend + frontend) ---

.PHONY: dev backend frontend migrate

# Launch both services via the helper script (preferred)
dev:
	./scripts/dev.sh

# Run just the backend (FastAPI/uvicorn)
backend:
	python -m uvicorn src.api.app:app --reload --port 8000

# Run just the frontend (Vite)
frontend:
	cd frontend && npm run dev

# Apply latest DB migrations
migrate:
	python -m alembic upgrade head