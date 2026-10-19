# Contributing

## Setup

```bash
make install            # uv sync + pre-commit hooks (ruff, mypy, conventional commits)
brew install k6         # or https://grafana.com/docs/k6/latest/set-up/install-k6/
cp .env.example .env    # optional: point at another API
```

## Local gate

```bash
make lint               # ruff + mypy --strict
make functional         # pytest -n 4, JUnit in reports/
make contract           # Schemathesis + pinned known gaps
make perf               # k6 smoke, thresholds fail the command
```

Or the same thing without a toolchain: `make docker-test` and `make docker-perf`.

## Commit messages

Conventional Commits, enforced by the `commit-msg` hook: `feat`, `fix`, `test`, `ci`, `build`,
`docs`, `chore`, `refactor`, `perf`.

## Where things go

| Change                                  | Location                           | Rule                                                          |
| --------------------------------------- | ---------------------------------- | ------------------------------------------------------------- |
| A response shape                        | `schemas/<name>.schema.json`       | Draft 2020-12, `additionalProperties: false`, `$ref` by file  |
| An endpoint call                        | `src/api_quality_toolkit/client.py`| Return `httpx.Response`; no assertions in the client          |
| A functional test                       | `tests/functional/`                | Mark `smoke`/`regression`; `destructive` if it writes         |
| Contract scope or budget                | `tests/contract/test_openapi_contract.py` | Read-only, positive data, core checks                  |
| A sandbox bug you must live with        | `tests/contract/known_gaps.py`     | Reproduce it; it is pinned as an xfail, not silenced          |
| A latency/error budget                  | `perf/k6/smoke.js` thresholds      | Per-endpoint `p(95)` + global error rate; CI reads env vars   |

## Rejected in review

- `time.sleep` / polling loops in tests.
- Asserting on fields the schema does not declare (add them to the schema first).
- Raising `CONTRACT_MAX_EXAMPLES` in CI without a reason - the sandbox is shared.
