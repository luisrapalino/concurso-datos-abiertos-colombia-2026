import httpx

from modules.epidemiological_surveillance.application.normalization import (
    epidemiological_week_period,
    normalize_indicator_value,
    normalize_territorial_code,
)
from modules.epidemiological_surveillance.domain.records import RawHealthIndicatorRecord
from shared.socrata_client import SocrataHttpClient

DEFAULT_BASE_URL = "https://www.datos.gov.co/resource/4hyg-wa9d.json"
DENGUE_EVENT_CODE = "210"
DEFAULT_TIMEOUT_SECONDS = 180.0
SIVIGILA_SELECT = "cod_mun_o,municipio_ocurrencia,ano,semana,conteo"


class SivigilaSurveillanceClient:
    """HTTP client for SIVIGILA aggregated event counts on datos.gov.co."""

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        event_code: str = DENGUE_EVENT_CODE,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        socrata_client: SocrataHttpClient | None = None,
    ) -> None:
        self._base_url = base_url
        self._event_code = event_code
        self._socrata = socrata_client or SocrataHttpClient.from_settings(
            timeout_seconds=timeout_seconds,
        )

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
            "$select": SIVIGILA_SELECT,
            "cod_eve": self._event_code,
        }
        if year is not None:
            params["ano"] = str(year)
        if territorial_code is not None:
            params["cod_mun_o"] = territorial_code

        payload = self._socrata.get_json(self._base_url, params, http_client=http_client)
        if not isinstance(payload, list):
            msg = f"Expected list payload from Socrata API, got {type(payload)!r}"
            raise TypeError(msg)

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
