# One entry point for every environment. `make help` lists targets.
.DEFAULT_GOAL := help
REPORTS := reports

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies and git hooks
	uv sync
	uv run pre-commit install --hook-type pre-commit --hook-type commit-msg

lint: ## Ruff + mypy (strict)
	uv run ruff check . && uv run ruff format --check . && uv run mypy

smoke: ## Functional @smoke tests
	uv run pytest tests/functional -m smoke -q

functional: ## All functional tests, parallel, JUnit to reports/
	mkdir -p $(REPORTS) && uv run pytest tests/functional -n 4 -q --junitxml=$(REPORTS)/junit-functional.xml

contract: ## Schemathesis contract tests + pinned known gaps
	mkdir -p $(REPORTS) && uv run pytest tests/contract -q --junitxml=$(REPORTS)/junit-contract.xml

perf: ## k6 performance smoke with build-failing thresholds
	mkdir -p $(REPORTS) && k6 run perf/k6/smoke.js

test: lint functional contract ## Everything except perf

docker-build: ## Build the test image
	docker build -t api-quality-toolkit:local .

docker-test: docker-build ## Functional suite inside Docker
	docker compose run --rm tests tests/functional -q --junitxml=reports/junit-docker.xml

docker-perf: ## k6 smoke via the official grafana/k6 image
	docker compose run --rm k6

.PHONY: help install lint smoke functional contract perf test docker-build docker-test docker-perf
