"""Deterministic-but-unique request builders."""

from __future__ import annotations

import itertools
import time
from datetime import UTC, datetime, timedelta
from typing import Any

_seq = itertools.count(1)


def _stamp() -> str:
    return f"{int(time.time()):x}{next(_seq)}"


def iso_date(days_from_now: int) -> str:
    return (datetime.now(tz=UTC) + timedelta(days=days_from_now)).date().isoformat()


def booking(**overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "firstname": f"Aq{_stamp()}",
        "lastname": f"Toolkit{_stamp()}",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {"checkin": iso_date(7), "checkout": iso_date(10)},
        "additionalneeds": "Breakfast",
    }
    body.update(overrides)
    return body
