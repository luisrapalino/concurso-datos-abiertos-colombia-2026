import time

import httpx

from modules.epidemiological_surveillance.application.normalization import (
    epidemiological_week_period,
    normalize_indicator_value,
    normalize_territorial_code,
)
from modules.epidemiological_surveillance.domain.records import RawHealthIndicatorRecord

DEFAULT_BASE_URL = "https://www.datos.gov.co/resource/4hyg-wa9d.json"
DENGUE_EVENT_CODE = "210"
DEFAULT_TIMEOUT_SECONDS = 180.0
MAX_RETRIES = 5
RETRY_BACKOFF_SECONDS = 5.0


class SivigilaSurveillanceClient:
    """HTTP client for SIVIGILA aggregated event counts on datos.gov.co."""

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        event_code: str = DENGUE_EVENT_CODE,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        max_retries: int = MAX_RETRIES,
    ) -> None:
        self._base_url = base_url
        self._event_code = event_code
        self._timeout_seconds = timeout_seconds
        self._max_retries = max_retries

    def fetch_records(
        self,
        *,
        year: int | None = None,
        territorial_code: str | None = None,
        limit: int = 5000,
        offset: int = 0,
        http_client: httpx.Client | None = None,
    ) -> list[RawHealthIndicatorRecord]:
        params: dict[str, str | int] = {
            "$limit": limit,
            "$offset": offset,
            "$order": "cod_mun_o,ano,semana",
            "cod_eve": self._event_code,
        }
        if year is not None:
            params["ano"] = str(year)
        if territorial_code is not None:
            params["cod_mun_o"] = territorial_code

        response = self._get_with_retry(params, http_client=http_client)
        response.raise_for_status()
        payload = response.json()

        records: list[RawHealthIndicatorRecord] = []
        for row in payload:
            territorial_code = normalize_territorial_code(str(row["cod_mun_o"]))
            week = int(row["semana"])
            event_year = int(row["ano"])
            records.append(
                RawHealthIndicatorRecord(
                    territorial_code=territorial_code,
                    territory_name=str(row.get("municipio_ocurrencia", "")),
                    source_indicator_key=self._event_code,
                    period=epidemiological_week_period(event_year, week),
                    value=normalize_indicator_value(row["conteo"]),
                )
            )
        return records

    def _get_with_retry(
        self,
        params: dict[str, str | int],
        *,
        http_client: httpx.Client | None,
    ) -> httpx.Response:
        last_error: Exception | None = None
        for attempt in range(self._max_retries):
            try:
                if http_client is not None:
                    response = http_client.get(self._base_url, params=params)
                else:
                    with httpx.Client(timeout=self._timeout_seconds) as client:
                        response = client.get(self._base_url, params=params)
                if response.status_code < 500:
                    return response
                last_error = httpx.HTTPStatusError(
                    f"Server error '{response.status_code}'",
                    request=response.request,
                    response=response,
                )
            except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.NetworkError) as exc:
                last_error = exc
            if attempt + 1 >= self._max_retries:
                break
            time.sleep(RETRY_BACKOFF_SECONDS * (2**attempt))
        assert last_error is not None
        raise last_error
