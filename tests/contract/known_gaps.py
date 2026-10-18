"""Contract gaps observed in the public Swagger Petstore sandbox.

Each entry reproduces a spec violation with a plain request so the suite stays honest:
the fuzzer skips these operations, and `test_known_gaps.py` keeps checking the *correct*
behaviour as an expected failure. When the sandbox is fixed the xfail turns into XPASS,
which is the cue to delete the entry and let Schemathesis cover the operation again.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Gap:
    operation: str
    path: str
    expected: str
    observed: str
    params: dict[str, str] | None = None


KNOWN_GAPS: tuple[Gap, ...] = (
    Gap(
        operation="GET /store/inventory",
        path="/store/inventory",
        expected="200 with a JSON object of status -> quantity",
        observed="500 Internal Server Error",
    ),
    Gap(
        operation="GET /user/{username}",
        path="/user/definitely-not-a-user",
        expected="404 for an unknown username (declared in the spec)",
        observed="500 Internal Server Error",
    ),
    Gap(
        operation="GET /user/login",
        path="/user/login",
        params={"username": "user1", "password": "pass"},
        expected="application/json body (the spec declares a JSON string)",
        observed="Content-Type says JSON but the body is plain text 'Logged in user session: …'",
    ),
)

# Regex consumed by `schema.exclude(path_regex=...)`.
KNOWN_GAP_PATHS = r"^/(store/inventory|user/login|user/\{username\})$"
