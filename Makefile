.PHONY: help install install-no-dev lint lint-fix format-check format check fix

help:  ## Show this help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install:  ## Install all dependencies (with dev)
	uv sync

install-no-dev:  ## Install only production dependencies (no dev)
	uv sync --no-dev

run:  ## Run app Weather Parser Notifier (GUI by default)
	uv run python -m src.main

run-cli:  ## Run app in CLI mode
	uv run weather-cli

run-gui:  ## Run app in GUI mode
	uv run weather-gui

lint:  ## Check code for errors and style issues
	uv run ruff check .

lint-fix:  ## Fix automatically fixable linting issues
	uv run ruff check --fix .

format-check:  ## Check if code is properly formatted
	uv run ruff format --check .

format:  ## Auto-format code
	uv run ruff format .

check:  ## Run all checks (lint + format)
	lint format-check

fix:  ## Fix all issues (lint + format)
	lint-fix format
