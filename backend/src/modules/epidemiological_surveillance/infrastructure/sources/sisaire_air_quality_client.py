"""SISAIRE daily PM2.5 readings aggregated to municipal annual means (fallback source)."""

from __future__ import annotations

import re
import unicodedata
from collections import defaultdict
from decimal import Decimal

import httpx

from modules.epidemiological_surveillance.application.normalization import annual_period
from modules.epidemiological_surveillance.domain.records import RawHealthIndicatorRecord
from shared.divipola_catalog import DivipolaCatalog
from shared.municipal_dataset_catalog import API_AIR_SISAIRE

DEFAULT_BASE_URL = API_AIR_SISAIRE


class SisaireAirQualityClient:
    """Fallback client for yspz-pxxn when annual municipal aggregates are unavailable."""

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        territorial_catalog: DivipolaCatalog | None = None,
        timeout_seconds: float = 120.0,
    ) -> None:
        self._base_url = base_url
        self._territorial_catalog = territorial_catalog
        self._timeout_seconds = timeout_seconds

    def fetch_records(
        self,
        *,
        year: int | None = None,
        territorial_code: str | None = None,
        limit: int = 5000,
        offset: int = 0,
        http_client: httpx.Client | None = None,
    ) -> list[RawHealthIndicatorRecord]:
        if territorial_code is None or offset > 0:
            return []

        if self._territorial_catalog is None:
            msg = "DIVIPOLA catalog is required to resolve municipality station filters."
            raise ValueError(msg)

        normalized_code = territorial_code.strip().zfill(5)
        municipality_name = self._territorial_catalog.municipality_name(normalized_code)
        if municipality_name is None:
            return []

        search_token = _normalize_station_token(municipality_name)
        if not search_token:
            return []

        where_parts = [f"upper(estacion) like '%{search_token}%'"]
        if year is not None:
            where_parts.append(
                f"fecha_lectura >= '{year}-01-01T00:00:00.000' "
                f"AND fecha_lectura < '{year + 1}-01-01T00:00:00.000'",
            )

        params: dict[str, str | int] = {
            "$limit": limit,
            "$offset": offset,
            "$order": "fecha_lectura",
            "$where": " AND ".join(where_parts),
        }

        if http_client is not None:
            response = http_client.get(self._base_url, params=params)
        else:
            with httpx.Client(timeout=self._timeout_seconds) as client:
                response = client.get(self._base_url, params=params)

        response.raise_for_status()
        payload = response.json()
        if not payload:
            return []

        year_values: dict[int, list[Decimal]] = defaultdict(list)
        for row in payload:
            raw_date = str(row.get("fecha_lectura", ""))
            if len(raw_date) < 4:
                continue
            event_year = int(raw_date[:4])
            if year is not None and event_year != year:
                continue
            pm25 = row.get("pm25")
            if pm25 is None or str(pm25).strip() == "":
                pm25 = row.get("pm10")
            if pm25 is None or str(pm25).strip() == "":
                continue
            year_values[event_year].append(Decimal(str(pm25)))

        records: list[RawHealthIndicatorRecord] = []
        for event_year, values in sorted(year_values.items()):
            mean_value = sum(values) / len(values)
            records.append(
                RawHealthIndicatorRecord(
                    territorial_code=normalized_code,
                    territory_name=municipality_name,
                    source_indicator_key="pm25",
                    period=annual_period(event_year),
                    value=mean_value.quantize(Decimal("0.0001")),
                ),
            )
        return records


def _normalize_station_token(municipality_name: str) -> str:
    normalized = unicodedata.normalize("NFD", municipality_name.upper())
    without_accents = "".join(
        character for character in normalized if unicodedata.category(character) != "Mn"
    )
    cleaned = re.sub(r"[^A-Z0-9 ]", " ", without_accents)
    token = cleaned.split(",")[0].strip()
    return token.replace("  ", " ")
