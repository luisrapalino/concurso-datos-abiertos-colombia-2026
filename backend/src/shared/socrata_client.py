"""Shared HTTP client for datos.gov.co Socrata SODA API."""

from __future__ import annotations

import time
from typing import Any

import httpx

DEFAULT_TIMEOUT_SECONDS = 120.0
DEFAULT_MAX_RETRIES = 5
DEFAULT_RETRY_BACKOFF_SECONDS = 5.0
RETRYABLE_STATUS_CODES = frozenset({429, 500, 502, 503, 504})


class SocrataHttpClient:
    """HTTP helper with App Token, retries and rate-limit handling."""

    def __init__(
        self,
        *,
        app_token: str | None = None,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_backoff_seconds: float = DEFAULT_RETRY_BACKOFF_SECONDS,
    ) -> None:
        self._app_token = app_token
        self._timeout_seconds = timeout_seconds
        self._max_retries = max_retries
        self._retry_backoff_seconds = retry_backoff_seconds

    @classmethod
    def from_settings(cls, **kwargs: Any) -> SocrataHttpClient:
        from config.settings import get_settings

        settings = get_settings()
        return cls(app_token=settings.socrata_app_token, **kwargs)

    def _headers(self) -> dict[str, str]:
        if not self._app_token:
            return {}
        return {"X-App-Token": self._app_token}

    def get_json(
        self,
        url: str,
        params: dict[str, str | int],
        *,
        http_client: httpx.Client | None = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        response = self.get(url, params, http_client=http_client)
        response.raise_for_status()
        payload = response.json()
        if isinstance(payload, list | dict):
            return payload
        msg = f"Unexpected Socrata payload type: {type(payload)!r}"
        raise TypeError(msg)

    def get(
        self,
        url: str,
        params: dict[str, str | int],
        *,
        http_client: httpx.Client | None = None,
    ) -> httpx.Response:
        headers = self._headers()
        if http_client is not None:
            return self._request_with_retry(url, params, http_client=http_client, headers=headers)

        with httpx.Client(timeout=self._timeout_seconds, headers=headers) as client:
            return self._request_with_retry(url, params, http_client=client, headers=headers)

    def _request_with_retry(
        self,
        url: str,
        params: dict[str, str | int],
        *,
        http_client: httpx.Client,
        headers: dict[str, str],
    ) -> httpx.Response:
        last_error: Exception | None = None
        request_headers = headers or None

        for attempt in range(self._max_retries):
            try:
                response = http_client.get(url, params=params, headers=request_headers)
                if response.status_code not in RETRYABLE_STATUS_CODES:
                    return response
                last_error = httpx.HTTPStatusError(
                    f"Socrata HTTP {response.status_code}",
                    request=response.request,
                    response=response,
                )
            except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.NetworkError) as exc:
                last_error = exc

            if attempt + 1 >= self._max_retries:
                break

            delay = self._retry_backoff_seconds * (2**attempt)
            if isinstance(last_error, httpx.HTTPStatusError) and last_error.response is not None:
                raw_retry = last_error.response.headers.get("Retry-After")
                if raw_retry and raw_retry.isdigit():
                    delay = float(raw_retry)

            time.sleep(delay)

        assert last_error is not None
        if isinstance(last_error, httpx.HTTPStatusError) and last_error.response is not None:
            return last_error.response
        raise last_error
