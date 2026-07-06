import httpx

from modules.epidemiological_surveillance.application.normalization import (
    normalize_indicator_value,
    normalize_territorial_code,
)
from modules.epidemiological_surveillance.domain.records import RawMortalityIndicatorRecord
from shared.socrata_client import SocrataHttpClient

DEFAULT_BASE_URL = "https://www.datos.gov.co/resource/4e4i-ua65.json"
GENERAL_MORTALITY_INDICATOR = "TASA DE MORTALIDAD GENERAL"
INSTITUTIONAL_BIRTHS_INDICATOR = "PORCENTAJE DE PARTOS INSTITUCIONALES"
MORTALITY_SELECT = "codmunicipio,municipio,a_o,valor_indicador"


class DatosGovCoMortalityClient:
    """HTTP client for INS mortality indicators on datos.gov.co (Socrata API)."""

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        source_indicator_key: str = GENERAL_MORTALITY_INDICATOR,
        timeout_seconds: float = 60.0,
        socrata_client: SocrataHttpClient | None = None,
    ) -> None:
        self._base_url = base_url
        self._source_indicator_key = source_indicator_key
        self._socrata = socrata_client or SocrataHttpClient.from_settings(
            timeout_seconds=timeout_seconds,
        )

    def fetch_general_mortality_records(
        self,
        *,
        year: int | None = None,
        territorial_code: str | None = None,
        limit: int = 5000,
        offset: int = 0,
        http_client: httpx.Client | None = None,
    ) -> list[RawMortalityIndicatorRecord]:
        params: dict[str, str | int] = {
            "$limit": limit,
            "$offset": offset,
            "$order": "codmunicipio,a_o",
            "$select": MORTALITY_SELECT,
            "indicador": self._source_indicator_key,
        }
        if year is not None:
            params["a_o"] = str(year)
        if territorial_code is not None:
            params["codmunicipio"] = territorial_code

        payload = self._socrata.get_json(self._base_url, params, http_client=http_client)
        if not isinstance(payload, list):
            msg = f"Expected list payload from Socrata API, got {type(payload)!r}"
            raise TypeError(msg)

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
