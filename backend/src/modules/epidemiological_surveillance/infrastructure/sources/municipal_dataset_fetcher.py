from __future__ import annotations

from modules.epidemiological_surveillance.domain.records import RawHealthIndicatorRecord
from modules.epidemiological_surveillance.infrastructure.sources.air_quality_client import (
    AirQualityClient,
)
from modules.epidemiological_surveillance.infrastructure.sources.client_adapters import (
    MortalityIndicatorsClientAdapter,
)
from modules.epidemiological_surveillance.infrastructure.sources.datos_gov_co_client import (
    DatosGovCoMortalityClient,
)
from modules.epidemiological_surveillance.infrastructure.sources.sisaire_air_quality_client import (
    SisaireAirQualityClient,
)
from modules.epidemiological_surveillance.infrastructure.sources.sivigila_client import (
    SivigilaSurveillanceClient,
)
from modules.epidemiological_surveillance.infrastructure.sources.vaccination_client import (
    VaccinationCoverageClient,
)
from shared.divipola_catalog import DivipolaCatalog
from shared.municipal_dataset_catalog import ClientType, MunicipalDatasetBinding


class MunicipalDatasetFetcher:
    """Executes fetch calls for a concrete dataset binding and municipality."""

    def __init__(self, catalog: DivipolaCatalog) -> None:
        self._catalog = catalog

    def fetch(
        self,
        binding: MunicipalDatasetBinding,
        *,
        territorial_code: str,
        year: int | None,
        limit: int,
        offset: int,
    ) -> list[RawHealthIndicatorRecord]:
        client = self._build_client(binding.client_type, binding.source_indicator_key)
        return client.fetch_records(
            year=year,
            territorial_code=territorial_code,
            limit=limit,
            offset=offset,
        )

    def _build_client(
        self,
        client_type: ClientType,
        source_indicator_key: str,
    ) -> object:
        if client_type == "mortality":
            return MortalityIndicatorsClientAdapter(
                DatosGovCoMortalityClient(source_indicator_key=source_indicator_key),
            )
        if client_type == "sivigila":
            return SivigilaSurveillanceClient(event_code=source_indicator_key)
        if client_type == "vaccination":
            return VaccinationCoverageClient(
                vaccine_name=source_indicator_key,
                territorial_catalog=self._catalog,
            )
        if client_type == "air_quality_annual":
            return AirQualityClient(territorial_catalog=self._catalog)
        if client_type == "air_quality_sisaire":
            return SisaireAirQualityClient(territorial_catalog=self._catalog)
        msg = f"Unsupported municipal dataset client type: {client_type}"
        raise ValueError(msg)
