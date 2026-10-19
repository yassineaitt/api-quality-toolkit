"""Property-based contract tests generated from the target's OpenAPI document.

Schemathesis builds one Hypothesis strategy per operation from the spec, calls the live
API with generated inputs and checks the response against the spec. It is limited to
read-only operations and a small example budget so it stays polite to the public sandbox
and fast in CI; the budget is tunable via ``CONTRACT_MAX_EXAMPLES``.
"""

from __future__ import annotations

import pytest
import schemathesis
from hypothesis import HealthCheck, Phase
from hypothesis import settings as hypothesis_settings
from schemathesis.checks import CHECKS
from schemathesis.generation import GenerationMode

from api_quality_toolkit.config import settings
from tests.contract.known_gaps import KNOWN_GAP_PATHS

# What "honouring the contract" means here: declared status codes, declared content types,
# bodies that validate against the response schema, and never a 5xx. Positive data only -
# negative-data rejection and RFC-level checks (Allow headers, TRACE handling) are opinions
# about the server, not the contract, and are left to the full `schemathesis run` CLI.
CORE_CHECKS = [
    "not_a_server_error",
    "status_code_conformance",
    "content_type_conformance",
    "response_schema_conformance",
]

schema = schemathesis.openapi.from_url(settings.contract_schema_url)
schema.config.update(base_url=str(settings.contract_base_url).rstrip("/"))
schema.config.generation.update(modes=[GenerationMode.POSITIVE])
# Spec examples + property-based fuzzing; the "coverage" phase probes undeclared methods
# (TRACE/OPTIONS) and the "stateful" phase needs write operations, which are excluded here.
schema.config.phases.update(phases=["examples", "fuzzing"])
# Operations with documented, reproducible contract gaps are pinned in
# tests/contract/test_known_gaps.py instead of being fuzzed here.
schema = schema.include(method="GET").exclude(path_regex=KNOWN_GAP_PATHS)

pytestmark = pytest.mark.contract


@schema.parametrize()
@hypothesis_settings(
    max_examples=settings.contract_max_examples,
    deadline=None,
    phases=[Phase.explicit, Phase.generate],
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.filter_too_much],
)
def test_read_operations_honour_their_contract(case: schemathesis.Case) -> None:
    case.call_and_validate(checks=CHECKS.get_by_names(CORE_CHECKS))
