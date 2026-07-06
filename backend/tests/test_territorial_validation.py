from decimal import Decimal

from modules.epidemiological_surveillance.application.ingest_mortality_indicators import (
    IngestMortalityIndicatorsUseCase,
)
from modules.epidemiological_surveillance.application.normalization import (
    IngestMortalityIndicatorsCommand,
)
from modules.epidemiological_surveillance.application.validate_territorial_records import (
    partition_records_by_catalog,
)
from modules.epidemiological_surveillance.domain.records import RawMortalityIndicatorRecord
from shared.divipola_catalog import DivipolaCatalog, TerritorialValidationSummary


class _FakeCatalog:
    source_id = "test-catalog"
    synced_at = "2026-01-01T00:00:00+00:00"
    municipality_count = 2

    def is_valid_municipality(self, code: str) -> bool:
        return code in {"05001", "05002"}


def test_divipola_catalog_loads_bundled_municipalities() -> None:
    catalog = DivipolaCatalog.from_file()
    assert catalog.source_id == "dane-divipola"
    assert catalog.municipality_count >= 1000
    assert catalog.is_valid_municipality("05001")
    assert catalog.municipality_name("05001") == "MEDELLÍN"


def test_partition_records_by_catalog_rejects_unknown_codes() -> None:
    records = [
        RawMortalityIndicatorRecord(
            territorial_code="05001",
            territory_name="Medellín",
            source_indicator_key="TASA DE MORTALIDAD GENERAL",
            year=2020,
            value=Decimal("1.0"),
        ),
        RawMortalityIndicatorRecord(
            territorial_code="99999",
            territory_name="Invalid",
            source_indicator_key="TASA DE MORTALIDAD GENERAL",
            year=2020,
            value=Decimal("2.0"),
        ),
    ]

    accepted, summary = partition_records_by_catalog(records, _FakeCatalog())

    assert len(accepted) == 1
    assert accepted[0].territorial_code == "05001"
    assert summary == TerritorialValidationSummary(
        accepted_count=1,
        rejected_count=1,
        rejected_territorial_codes=("99999",),
    )


def test_ingestion_use_case_reports_rejected_records_on_dry_run() -> None:
    class _SourceClient:
        def fetch_general_mortality_records(self, **kwargs):
            del kwargs
            return [
                RawMortalityIndicatorRecord(
                    territorial_code="05001",
                    territory_name="Medellín",
                    source_indicator_key="TASA DE MORTALIDAD GENERAL",
                    year=2020,
                    value=Decimal("1.0"),
                ),
                RawMortalityIndicatorRecord(
                    territorial_code="99999",
                    territory_name="Invalid",
                    source_indicator_key="TASA DE MORTALIDAD GENERAL",
                    year=2020,
                    value=Decimal("2.0"),
                ),
            ]

    class _Repository:
        def begin_run(self, source_id: str, *, sync_mode: str | None = None) -> str:
            del source_id, sync_mode
            return "run-id"

        def complete_run(self, run_id: str, **kwargs) -> None:
            del run_id, kwargs

        def fail_run(self, run_id: str, error_message: str) -> None:
            del run_id, error_message

        def upsert_observations(self, **kwargs) -> int:
            del kwargs
            return 0

    use_case = IngestMortalityIndicatorsUseCase(
        source_client=_SourceClient(),
        repository=_Repository(),
        territorial_catalog=_FakeCatalog(),
    )
    result = use_case.execute(
        IngestMortalityIndicatorsCommand(
            source_id="datos-gov-mortality-indicators",
            definition_id="general-mortality-rate",
            source_indicator_key="TASA DE MORTALIDAD GENERAL",
            year=2020,
            dry_run=True,
        ),
    )

    assert result.records_upserted == 1
    assert result.records_rejected == 1
    assert result.rejected_territorial_codes == ("99999",)
