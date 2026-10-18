from typing import Any

import pytest

from api_quality_toolkit.client import BookingClient
from api_quality_toolkit.data import booking as build_booking

pytestmark = pytest.mark.regression


def test_get_unknown_id_is_404(api: BookingClient) -> None:
    assert api.get(2_147_483_000).status_code == 404


def test_write_without_token_is_403(api: BookingClient, booking: dict[str, Any]) -> None:
    assert api.with_token(None).update(booking["bookingid"], build_booking()).status_code == 403
    assert api.with_token(None).delete(booking["bookingid"]).status_code == 403


def test_write_with_invalid_token_is_403(api: BookingClient, booking: dict[str, Any]) -> None:
    res = api.with_token("0000000deadbeef").patch(booking["bookingid"], {"firstname": "x"})
    api.with_token(None)

    assert res.status_code == 403


@pytest.mark.parametrize(
    "missing", ["firstname", "lastname", "totalprice", "depositpaid", "bookingdates"]
)
def test_create_without_required_field_is_rejected(api: BookingClient, missing: str) -> None:
    body = build_booking()
    del body[missing]

    res = api.create(body)

    assert res.status_code == 500, "service rejects incomplete payloads (with a 500, by design)"
    assert res.text == "Internal Server Error"
