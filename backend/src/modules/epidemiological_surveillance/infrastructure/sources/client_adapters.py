from modules.epidemiological_surveillance.domain.records import RawHealthIndicatorRecord
from modules.epidemiological_surveillance.infrastructure.sources.datos_gov_co_client import (
    DatosGovCoMortalityClient,
)


class MortalityIndicatorsClientAdapter:
    """Adapts the mortality client to the generic health indicators protocol."""

    def __init__(self, client: DatosGovCoMortalityClient) -> None:
        self._client = client

    def fetch_records(
        self,
        *,
        year: int | None = None,
        territorial_code: str | None = None,
        limit: int = 5000,
        offset: int = 0,
    ) -> list[RawHealthIndicatorRecord]:
        return [
            record.to_health_record()
            for record in self._client.fetch_general_mortality_records(
                year=year,
                territorial_code=territorial_code,
                limit=limit,
                offset=offset,
            )
        ]
