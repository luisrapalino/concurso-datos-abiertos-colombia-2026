from decimal import Decimal

import httpx

from modules.epidemiological_surveillance.application.normalization import annual_period
from modules.epidemiological_surveillance.domain.records import RawHealthIndicatorRecord
from shared.divipola_catalog import DivipolaCatalog
from shared.featured_municipalities import is_featured_municipality

DEFAULT_BASE_URL = "https://www.datos.gov.co/resource/6i25-2hdt.json"
PENTAVALENT_VACCINE = "PENTA3"


class VaccinationCoverageClient:
    """HTTP client for departmental vaccination coverage on datos.gov.co."""

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        vaccine_name: str = PENTAVALENT_VACCINE,
        territorial_catalog: DivipolaCatalog | None = None,
        timeout_seconds: float = 120.0,
    ) -> None:
        self._base_url = base_url
        self._vaccine_name = vaccine_name
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
        params: dict[str, str | int] = {
            "$limit": limit,
            "$offset": offset,
            "$order": "coddepto,a_o",
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

        if self._territorial_catalog is None:
            msg = "DIVIPOLA catalog is required to expand departmental vaccination coverage."
            raise ValueError(msg)

        target_department: str | None = None
        target_municipality: str | None = None
        if territorial_code is not None:
            target_municipality = territorial_code.strip().zfill(5)
            municipality = self._territorial_catalog.get_municipality(target_municipality)
            if municipality is None:
                return []
            target_department = str(municipality.get("department_code", "")).zfill(2)

        vaccine_token = _normalize_vaccine_token(self._vaccine_name)
        records: list[RawHealthIndicatorRecord] = []
        for row in payload:
            vaccine_label = str(row.get("biol_gico", ""))
            if vaccine_token not in _normalize_vaccine_token(vaccine_label):
                continue
            department_code = str(row["coddepto"]).strip().zfill(2)
            if target_department is not None and department_code != target_department:
                continue
            coverage = _normalize_coverage(row["cobertura_de_vacunaci_n"])
            event_year = int(row["a_o"])
            period = annual_period(event_year)
            municipality_codes = self._territorial_catalog.municipality_codes_for_department(
                department_code,
            )
            for municipality_code in municipality_codes:
                if target_municipality is not None and municipality_code != target_municipality:
                    continue
                if not is_featured_municipality(municipality_code):
                    continue
                records.append(
                    RawHealthIndicatorRecord(
                        territorial_code=municipality_code,
                        territory_name=str(row.get("departamento", "")),
                        source_indicator_key=vaccine_label,
                        period=period,
                        value=coverage,
                    )
                )
        return records


def _normalize_vaccine_token(value: str) -> str:
    normalized = value.upper()
    for old, new in (("Á", "A"), ("É", "E"), ("Í", "I"), ("Ó", "O"), ("Ú", "U"), ("Ñ", "N"), ("Ã", "A")):
        normalized = normalized.replace(old, new)
    return normalized


def _normalize_coverage(raw_value: str | float) -> Decimal:
    value = float(str(raw_value).replace(",", "."))
    if 0 < value <= 1:
        value *= 100
    if value > 100:
        return Decimal("100")
    if value < 0:
        return Decimal("0")
    return Decimal(str(round(value, 4)))
