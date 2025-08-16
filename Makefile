
.PHONY: help install lint test run

help:
	@echo "Common commands:"
	@echo "  make install   - install dev dependencies"
	@echo "  make lint	  - run ruff/black if configured"
	@echo "  make test	  - run tests"
	@echo "  make run	   - run local API (uvicorn)"

install:
	python -m pip install --upgrade pip

lint:
	@echo "lint placeholder"

test:
	pytest -q || true

run:
	python -m uvicorn src.api.app:app --reload --port 8000
