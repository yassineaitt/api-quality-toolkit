"""Pin documented sandbox contract gaps as expected failures (see known_gaps.py)."""

from __future__ import annotations

import json

import httpx
import pytest
from tests.contract.known_gaps import KNOWN_GAPS, Gap

from api_quality_toolkit.config import settings

pytestmark = pytest.mark.contract


@pytest.fixture(scope="module")
def petstore() -> httpx.Client:
    return httpx.Client(
        base_url=str(settings.contract_base_url).rstrip("/"),
        headers={"Accept": "application/json"},
        timeout=settings.timeout_s,
    )


@pytest.mark.parametrize("gap", KNOWN_GAPS, ids=[g.operation for g in KNOWN_GAPS])
@pytest.mark.xfail(reason="documented contract gap in the public sandbox", strict=False)
def test_operation_honours_contract(petstore: httpx.Client, gap: Gap) -> None:
    res = petstore.get(gap.path, params=gap.params)

    assert res.status_code < 500, f"{gap.operation}: expected {gap.expected}, got {res.status_code}"
    if gap.path.startswith("/user/definitely"):
        assert res.status_code == 404
    assert res.headers.get("content-type", "").startswith("application/json")
    try:
        json.loads(res.text)
    except json.JSONDecodeError as exc:
        msg = f"{gap.operation}: body is not JSON ({gap.observed})"
        raise AssertionError(msg) from exc
