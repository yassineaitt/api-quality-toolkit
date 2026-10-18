"""JSON Schema validation with readable failures.

Schemas live in ``schemas/*.schema.json`` (Draft 2020-12) and are loaded once per process.
``assert_matches`` raises an ``AssertionError`` listing every violation with its JSON path,
so a contract drift reads as a test failure, not a stack trace.
"""

from __future__ import annotations

import json
from functools import cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

SCHEMA_DIR = Path(__file__).resolve().parents[2] / "schemas"


@cache
def load_schema(name: str) -> dict[str, Any]:
    path = SCHEMA_DIR / f"{name}.schema.json"
    schema: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return schema


def violations(instance: Any, schema_name: str) -> list[str]:
    validator = Draft202012Validator(load_schema(schema_name))
    out: list[str] = []
    for err in sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path)):
        where = "/".join(str(p) for p in err.absolute_path) or "<root>"
        out.append(f"{where}: {err.message}")
    return out


def assert_matches(instance: Any, schema_name: str) -> None:
    problems = violations(instance, schema_name)
    if problems:
        joined = "\n  - ".join(problems)
        msg = f"response does not match schema '{schema_name}':\n  - {joined}"
        raise AssertionError(msg)
