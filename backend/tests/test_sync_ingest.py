"""Tests for incremental sync ingestion."""

from decimal import Decimal

from modules.epidemiological_surveillance.application.normalization import (
    SyncIngestHealthIndicatorsCommand,
)
from modules.epidemiological_surveillance.application.sync_ingest_health_indicators import (
    SyncIngestHealthIndicatorsUseCase,
    resolve_sync_years,
)
from modules.epidemiological_surveillance.domain.records import RawHealthIndicatorRecord


class _FakeSourceClient:
    def __init__(self, batches: dict[tuple[int, str | None, int], list[RawHealthIndicatorRecord]]) -> None:
        self._batches = batches
        self.calls: list[tuple[int | None, str | None, int, int]] = []

    def fetch_records(
        self,
        *,
        year: int | None = None,
        territorial_code: str | None = None,
        limit: int = 5000,
        offset: int = 0,
    ) -> list[RawHealthIndicatorRecord]:
        self.calls.append((year, territorial_code, limit, offset))
        return self._batches.get((year or 0, territorial_code, offset), [])


class _FakeRepository:
    def __init__(self) -> None:
        self.upserted: list[int] = []

    def begin_run(self, source_id: str, *, sync_mode: str | None = None) -> str:
        return f"run:{source_id}"

    def complete_run(self, run_id: str, **kwargs) -> None:
        del run_id, kwargs

    def fail_run(self, run_id: str, error_message: str) -> None:
        del run_id, error_message

    def upsert_observations(self, **kwargs) -> int:
        records = kwargs["records"]
        self.upserted.append(len(records))
        return len(records)


def _record(code: str, period: str) -> RawHealthIndicatorRecord:
    return RawHealthIndicatorRecord(
        territorial_code=code,
        territory_name="TEST",
        source_indicator_key="210",
        period=period,
        value=Decimal("1"),
    )


def test_resolve_sync_years_orders_from_start_to_end_desc() -> None:
    assert resolve_sync_years(2022, 2020) == (2022, 2021, 2020)


def test_sync_ingest_paginates_per_municipality_and_year() -> None:
    client = _FakeSourceClient(
        {
            (2022, "05001", 0): [_record("05001", "2022-W01")],
            (2022, "05001", 1): [],
            (2022, "11001", 0): [_record("11001", "2022-W01"), _record("11001", "2022-W02")],
            (2022, "11001", 2): [],
            (2021, "05001", 0): [],
            (2021, "11001", 0): [],
        }
    )
    repository = _FakeRepository()
    use_case = SyncIngestHealthIndicatorsUseCase(client, repository)

    result = use_case.execute(
        SyncIngestHealthIndicatorsCommand(
            source_id="datos-gov-sivigila",
            definition_id="dengue-weekly-cases",
            source_indicator_key="210",
            sync_strategy="per_municipality",
            batch_size=2,
            start_year=2022,
            end_year=2021,
            territorial_codes=("05001", "11001"),
        )
    )

    assert result.records_upserted == 3
    assert result.batches_processed == 2
    assert result.years_processed == (2022,)
    assert repository.upserted == [1, 2]


def test_sync_ingest_by_year_strategy() -> None:
    client = _FakeSourceClient(
        {
            (2020, None, 0): [_record("05001", "2020-01")],
            (2020, None, 1): [],
        }
    )
    repository = _FakeRepository()
    use_case = SyncIngestHealthIndicatorsUseCase(client, repository)

    result = use_case.execute(
        SyncIngestHealthIndicatorsCommand(
            source_id="datos-gov-mortality-indicators",
            definition_id="general-mortality-rate",
            source_indicator_key="TASA DE MORTALIDAD GENERAL",
            sync_strategy="by_year",
            batch_size=1000,
            start_year=2020,
            end_year=2020,
        )
    )

    assert result.records_upserted == 1
    assert client.calls[0][1] is None
