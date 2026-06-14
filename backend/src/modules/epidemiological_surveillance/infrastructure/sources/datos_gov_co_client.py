import httpx

from modules.epidemiological_surveillance.application.normalization import (
    normalize_indicator_value,
    normalize_territorial_code,
)
from modules.epidemiological_surveillance.domain.records import RawMortalityIndicatorRecord

DEFAULT_BASE_URL = "https://www.datos.gov.co/resource/4e4i-ua65.json"
GENERAL_MORTALITY_INDICATOR = "TASA DE MORTALIDAD GENERAL"


class DatosGovCoMortalityClient:
    """HTTP client for INS mortality indicators on datos.gov.co (Socrata API)."""

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        source_indicator_key: str = GENERAL_MORTALITY_INDICATOR,
        timeout_seconds: float = 60.0,
    ) -> None:
        self._base_url = base_url
        self._source_indicator_key = source_indicator_key
        self._timeout_seconds = timeout_seconds

    def fetch_general_mortality_records(
        self,
        *,
        year: int | None = None,
        limit: int = 5000,
        offset: int = 0,
        http_client: httpx.Client | None = None,
    ) -> list[RawMortalityIndicatorRecord]:
        params: dict[str, str | int] = {
            "$limit": limit,
            "$offset": offset,
            "$order": "codmunicipio,a_o",
            "indicador": self._source_indicator_key,
        }
        if year is not None:
            params["a_o"] = str(year)

        if http_client is not None:
            response = http_client.get(self._base_url, params=params)
        else:
            with httpx.Client(timeout=self._timeout_seconds) as client:
                response = client.get(self._base_url, params=params)

        response.raise_for_status()
        payload = response.json()

        records: list[RawMortalityIndicatorRecord] = []
        for row in payload:
            territorial_code = normalize_territorial_code(str(row["codmunicipio"]))
            records.append(
                RawMortalityIndicatorRecord(
                    territorial_code=territorial_code,
                    territory_name=str(row.get("municipio", "")),
                    source_indicator_key=self._source_indicator_key,
                    year=int(row["a_o"]),
                    value=normalize_indicator_value(row["valor_indicador"]),
                )
            )
        return records
