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
from referencing import Registry, Resource

SCHEMA_DIR = Path(__file__).resolve().parents[2] / "schemas"


@cache
def load_schema(name: str) -> dict[str, Any]:
    path = SCHEMA_DIR / f"{name}.schema.json"
    schema: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return schema


@cache
def registry() -> Registry[Any]:
    """All schemas in the directory, so `$ref: "<file>.schema.json"` resolves offline."""
    resources = [
        (path.name, Resource.from_contents(json.loads(path.read_text(encoding="utf-8"))))
        for path in sorted(SCHEMA_DIR.glob("*.schema.json"))
    ]
    reg: Registry[Any] = Registry()
    for name, resource in resources:
        reg = reg.with_resource(uri=name, resource=resource)
        reg = reg.with_resource(uri=str(resource.contents.get("$id", name)), resource=resource)
    return reg


def violations(instance: Any, schema_name: str) -> list[str]:
    validator = Draft202012Validator(load_schema(schema_name), registry=registry())
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
