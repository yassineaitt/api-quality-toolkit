## What

## Why

## How to verify

- [ ] `make lint`
- [ ] `make functional` and `make contract` against the public sandboxes
- [ ] `make perf` if `perf/k6/smoke.js` or thresholds changed

## Checklist

- [ ] New responses are validated with a schema in `schemas/`
- [ ] New tests carry `smoke` or `regression` (and `destructive` when they write)
- [ ] Known contract gaps updated in `tests/contract/known_gaps.py` with evidence
