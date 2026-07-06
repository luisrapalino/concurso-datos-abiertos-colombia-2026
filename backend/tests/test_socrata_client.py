"""Tests for shared Socrata HTTP client."""

import httpx
import pytest

from shared.socrata_client import SocrataHttpClient


def test_get_json_sends_app_token_header() -> None:
    captured_headers: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured_headers.update(dict(request.headers))
        return httpx.Response(200, json=[{"value": 1}])

    client = SocrataHttpClient(app_token="test-token")
    http_client = httpx.Client(transport=httpx.MockTransport(handler))
    payload = client.get_json("https://example.test/resource.json", {"$limit": 1}, http_client=http_client)

    assert payload == [{"value": 1}]
    assert captured_headers.get("x-app-token") == "test-token"


def test_get_retries_on_429_then_succeeds(monkeypatch) -> None:
    attempts = {"count": 0}
    sleeps: list[float] = []

    def fake_sleep(seconds: float) -> None:
        sleeps.append(seconds)

    monkeypatch.setattr("shared.socrata_client.time.sleep", fake_sleep)

    def handler(_request: httpx.Request) -> httpx.Response:
        attempts["count"] += 1
        if attempts["count"] == 1:
            return httpx.Response(429, headers={"Retry-After": "2"}, json={"error": "rate limit"})
        return httpx.Response(200, json=[])

    client = SocrataHttpClient(app_token=None, max_retries=3, retry_backoff_seconds=1.0)
    http_client = httpx.Client(transport=httpx.MockTransport(handler))
    payload = client.get_json("https://example.test/resource.json", {"$limit": 1}, http_client=http_client)

    assert payload == []
    assert attempts["count"] == 2
    assert sleeps == [2.0]
