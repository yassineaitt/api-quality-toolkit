# syntax=docker/dockerfile:1.7
# Functional + contract tests in a container. k6 runs from the official grafana/k6 image
# (see docker-compose.yml) so each tool keeps its own, minimal runtime.
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS base

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependency layer – cached unless the lockfile changes.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv uv sync --locked --no-install-project

# Source layer
COPY src ./src
COPY schemas ./schemas
COPY tests ./tests
RUN --mount=type=cache,target=/root/.cache/uv uv sync --locked

RUN useradd --create-home --uid 1001 tester && chown -R tester:tester /app
USER tester

ENTRYPOINT ["uv", "run", "--no-sync", "pytest"]
CMD ["tests/functional", "-m", "smoke", "-q"]
