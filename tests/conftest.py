"""Session-level fixtures shared by functional tests."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any

import pytest

from api_quality_toolkit.client import BookingClient
from api_quality_toolkit.config import Settings
from api_quality_toolkit.config import settings as default_settings
from api_quality_toolkit.data import booking as build_booking
from api_quality_toolkit.validation import assert_matches


@pytest.fixture(scope="session")
def settings() -> Settings:
    return default_settings


@pytest.fixture(scope="session")
def api(settings: Settings) -> Iterator[BookingClient]:
    client = BookingClient(settings)
    yield client
    client.close()


@pytest.fixture(scope="session")
def authed_api(settings: Settings) -> Iterator[BookingClient]:
    client = BookingClient(settings)
    res = client.authenticate()
    assert res.status_code == 200, f"sandbox auth failed: {res.text}"
    yield client
    client.close()


@pytest.fixture
def create_booking(
    api: BookingClient, authed_api: BookingClient
) -> Iterator[Callable[..., dict[str, Any]]]:
    """Factory that validates the create response and deletes everything it made at teardown."""
    created: list[int] = []

    def _create(**overrides: Any) -> dict[str, Any]:
        res = api.create(build_booking(**overrides))
        assert res.status_code == 200, res.text
        body: dict[str, Any] = res.json()
        assert_matches(body, "created-booking")
        created.append(body["bookingid"])
        return body

    yield _create
    for booking_id in created:
        authed_api.delete(booking_id)


@pytest.fixture
def booking(create_booking: Callable[..., dict[str, Any]]) -> dict[str, Any]:
    return create_booking()
