import pytest

from api_quality_toolkit.client import BookingClient
from api_quality_toolkit.validation import assert_matches


@pytest.mark.smoke
def test_auth_issues_token_matching_contract(api: BookingClient) -> None:
    res = api.authenticate()

    assert res.status_code == 200
    assert res.headers["content-type"].startswith("application/json")
    assert_matches(res.json(), "auth-token")


@pytest.mark.regression
def test_auth_rejects_bad_credentials_with_reason(api: BookingClient) -> None:
    res = api.authenticate(password="wrong-password")

    assert res.status_code == 200  # documented service behaviour: 200 + reason, not 401
    assert res.json() == {"reason": "Bad credentials"}
