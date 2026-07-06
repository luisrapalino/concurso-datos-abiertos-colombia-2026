from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

import httpx

from modules.epidemiological_surveillance.application.normalization import annual_period
from modules.epidemiological_surveillance.domain.records import RawHealthIndicatorRecord
from shared.divipola_catalog import DivipolaCatalog
from shared.featured_municipalities import FEATURED_MUNICIPALITY_CODES
from shared.socrata_client import SocrataHttpClient

DEFAULT_BASE_URL = "https://www.datos.gov.co/resource/kekd-7v7h.json"
PM25_VARIABLE = "PM2.5"
DAILY_EXPOSURE_HOURS = "24"
AIR_QUALITY_SELECT = "a_o,promedio,nombre_del_municipio,id_estacion"


class AirQualityClient:
    """HTTP client for municipal PM2.5 annual means on datos.gov.co."""

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        territorial_catalog: DivipolaCatalog | None = None,
        timeout_seconds: float = 120.0,
        socrata_client: SocrataHttpClient | None = None,
    ) -> None:
        self._base_url = base_url
        self._territorial_catalog = territorial_catalog
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
        if territorial_code is None:
            records: list[RawHealthIndicatorRecord] = []
            for code in FEATURED_MUNICIPALITY_CODES:
                records.extend(
                    self.fetch_records(
                        year=year,
                        territorial_code=code,
                        limit=limit,
                        offset=0,
                        http_client=http_client,
                    ),
                )
            return records[:limit]

        if offset > 0:
            return []

        params: dict[str, str | int] = {
            "$limit": limit,
            "$offset": offset,
            "$order": "a_o, id_estacion",
            "$select": AIR_QUALITY_SELECT,
            "$where": _build_where_clause(
                territorial_code=territorial_code,
                year=year,
            ),
        }

        payload = self._socrata.get_json(self._base_url, params, http_client=http_client)
        if not isinstance(payload, list) or not payload:
            return []

        normalized_code = territorial_code.strip().zfill(5)
        municipality_name = (
            self._territorial_catalog.municipality_name(normalized_code)
            if self._territorial_catalog is not None
            else str(payload[0].get("nombre_del_municipio", normalized_code))
        )

        year_values: dict[int, list[Decimal]] = defaultdict(list)
        for row in payload:
            event_year = int(row["a_o"])
            if year is not None and event_year != year:
                continue
            raw_average = row.get("promedio")
            if raw_average is None or str(raw_average).strip() == "":
                continue
            year_values[int(row["a_o"])].append(Decimal(str(raw_average)))

        records: list[RawHealthIndicatorRecord] = []
        for event_year, values in sorted(year_values.items()):
            mean_value = sum(values) / len(values)
            records.append(
                RawHealthIndicatorRecord(
                    territorial_code=normalized_code,
                    territory_name=municipality_name or normalized_code,
                    source_indicator_key="pm25",
                    period=annual_period(event_year),
                    value=mean_value.quantize(Decimal("0.0001")),
                )
            )
        return records


def _build_where_clause(*, territorial_code: str, year: int | None) -> str:
    open_data_code = open_data_municipality_code(territorial_code)
    clauses = [
        f"c_digo_del_municipio = '{open_data_code}'",
        f"variable = '{PM25_VARIABLE}'",
        f"tiempo_de_exposici_n_horas = '{DAILY_EXPOSURE_HOURS}'",
    ]
    if year is not None:
        clauses.append(f"a_o = '{year}'")
    return " AND ".join(clauses)


def open_data_municipality_code(territorial_code: str) -> str:
    """Map DIVIPOLA 5-digit code to the numeric format used in kekd-7v7h."""
    return str(int(territorial_code.strip().zfill(5)))
