from collections.abc import Callable
from typing import Any

import pytest

from api_quality_toolkit.client import BookingClient
from api_quality_toolkit.data import booking as build_booking
from api_quality_toolkit.validation import assert_matches

pytestmark = pytest.mark.destructive


@pytest.mark.smoke
def test_create_echoes_payload_with_id(create_booking: Callable[..., dict[str, Any]]) -> None:
    payload = build_booking(totalprice=321, depositpaid=False)

    created = create_booking(**payload)

    assert created["booking"] == payload
    assert created["bookingid"] > 0


@pytest.mark.smoke
def test_get_returns_the_created_booking(api: BookingClient, booking: dict[str, Any]) -> None:
    res = api.get(booking["bookingid"])

    assert res.status_code == 200
    assert_matches(res.json(), "booking")
    assert res.json() == booking["booking"]


@pytest.mark.smoke
def test_list_filters_by_name(api: BookingClient, booking: dict[str, Any]) -> None:
    names = booking["booking"]
    res = api.list(firstname=names["firstname"], lastname=names["lastname"])

    assert res.status_code == 200
    assert_matches(res.json(), "booking-id-list")
    assert {"bookingid": booking["bookingid"]} in res.json()


@pytest.mark.regression
def test_put_replaces_booking(authed_api: BookingClient, booking: dict[str, Any]) -> None:
    replacement = build_booking(totalprice=999)

    res = authed_api.update(booking["bookingid"], replacement)

    assert res.status_code == 200
    assert_matches(res.json(), "booking")
    assert res.json() == replacement


@pytest.mark.regression
def test_patch_updates_single_field(
    api: BookingClient, authed_api: BookingClient, booking: dict[str, Any]
) -> None:
    res = authed_api.patch(booking["bookingid"], {"firstname": "Patched"})

    assert res.status_code == 200
    assert_matches(res.json(), "booking")
    assert res.json() == {**booking["booking"], "firstname": "Patched"}
    assert api.get(booking["bookingid"]).json()["firstname"] == "Patched"


@pytest.mark.regression
def test_delete_then_get_is_404(
    api: BookingClient, authed_api: BookingClient, create_booking: Callable[..., dict[str, Any]]
) -> None:
    booking_id = create_booking()["bookingid"]

    assert authed_api.delete(booking_id).status_code == 201  # service convention
    assert api.get(booking_id).status_code == 404
