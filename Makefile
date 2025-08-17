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
