"""A small httpx wrapper: base URL, JSON headers, token handling.

It returns raw ``httpx.Response`` objects so tests own every assertion; the only
behaviour it adds is the restful-booker auth convention (token cookie on writes).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from api_quality_toolkit.config import Settings


@dataclass
class BookingClient:
    settings: Settings
    _http: httpx.Client | None = None
    _token: str | None = None

    @property
    def http(self) -> httpx.Client:
        if self._http is None:
            self._http = httpx.Client(
                base_url=str(self.settings.api_base_url).rstrip("/"),
                headers={"Accept": "application/json"},
                timeout=self.settings.timeout_s,
            )
        return self._http

    def close(self) -> None:
        if self._http is not None:
            self._http.close()

    # ---- auth ---------------------------------------------------------------

    def authenticate(
        self, username: str | None = None, password: str | None = None
    ) -> httpx.Response:
        res = self.http.post(
            "/auth",
            json={
                "username": username or self.settings.api_username,
                "password": password or self.settings.api_password,
            },
        )
        if res.is_success and "token" in res.json():
            self._token = res.json()["token"]
        return res

    def with_token(self, token: str | None) -> BookingClient:
        self._token = token
        return self

    @property
    def _auth_headers(self) -> dict[str, str]:
        return {"Cookie": f"token={self._token}"} if self._token else {}

    # ---- bookings -----------------------------------------------------------

    def ping(self) -> httpx.Response:
        return self.http.get("/ping")

    def list(self, **params: str) -> httpx.Response:
        return self.http.get("/booking", params=params)

    def get(self, booking_id: int) -> httpx.Response:
        return self.http.get(f"/booking/{booking_id}")

    def create(self, body: dict[str, Any]) -> httpx.Response:
        return self.http.post("/booking", json=body)

    def update(self, booking_id: int, body: dict[str, Any]) -> httpx.Response:
        return self.http.put(f"/booking/{booking_id}", json=body, headers=self._auth_headers)

    def patch(self, booking_id: int, body: dict[str, Any]) -> httpx.Response:
        return self.http.patch(f"/booking/{booking_id}", json=body, headers=self._auth_headers)

    def delete(self, booking_id: int) -> httpx.Response:
        return self.http.delete(f"/booking/{booking_id}", headers=self._auth_headers)


def elapsed_ms(response: httpx.Response) -> float:
    """Wall-clock time of a completed (fully read) response, for latency assertions."""
    return response.elapsed.total_seconds() * 1000
