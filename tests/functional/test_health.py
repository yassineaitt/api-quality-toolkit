import pytest

from api_quality_toolkit.client import BookingClient, elapsed_ms


@pytest.mark.smoke
def test_ping_is_healthy_and_fast(api: BookingClient) -> None:
    res = api.ping()

    assert res.status_code == 201  # restful-booker answers 201 on /ping
    assert elapsed_ms(res) < 5_000
