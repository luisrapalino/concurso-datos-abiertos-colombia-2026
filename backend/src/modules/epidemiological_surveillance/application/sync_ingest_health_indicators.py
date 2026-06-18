from __future__ import annotations

from datetime import UTC, datetime

from collections.abc import Callable

from modules.epidemiological_surveillance.application.normalization import (
    SyncIngestHealthIndicatorsCommand,
)
from modules.epidemiological_surveillance.application.validate_territorial_records import (
    partition_records_by_catalog,
)
from modules.epidemiological_surveillance.domain.records import RawHealthIndicatorRecord
from modules.epidemiological_surveillance.domain.repositories import (
    HealthIndicatorsSourceClient,
    IngestionRepository,
    SyncIngestionResult,
)
from shared.divipola_catalog import TerritorialCatalog, TerritorialValidationSummary
from shared.featured_municipalities import FEATURED_MUNICIPALITY_CODES


class SyncIngestHealthIndicatorsUseCase:
    """Incremental ingestion: paginate open data by year and municipality, persisting each batch."""

    def __init__(
        self,
        source_client: HealthIndicatorsSourceClient,
        repository: IngestionRepository,
        *,
        territorial_catalog: TerritorialCatalog | None = None,
    ) -> None:
        self._source_client = source_client
        self._repository = repository
        self._territorial_catalog = territorial_catalog

    def execute(
        self,
        command: SyncIngestHealthIndicatorsCommand,
        *,
        progress: Callable[[str], None] | None = None,
    ) -> SyncIngestionResult:
        years = resolve_sync_years(command.start_year, command.end_year)
        territorial_codes = _resolve_territorial_iterations(command, self._territorial_catalog)
        batches_processed = 0
        total_upserted = 0
        total_rejected = 0
        rejected_codes: set[str] = set()
        years_touched: list[int] = []

        if command.dry_run:
            for year in years:
                for territorial_code in territorial_codes:
                    offset = 0
                    while True:
                        batch = self._fetch_batch(command, year, territorial_code, offset)
                        if not batch:
                            break
                        validated, summary = self._validate(command, batch)
                        total_upserted += len(validated)
                        total_rejected += summary.rejected_count
                        rejected_codes.update(summary.rejected_territorial_codes)
                        batches_processed += 1
                        if len(batch) < command.batch_size:
                            break
                        offset += len(batch)
                        if _should_stop(batches_processed, command.max_batches):
                            break
                    if _should_stop(batches_processed, command.max_batches):
                        break
                if year not in years_touched and batches_processed:
                    years_touched.append(year)
                if _should_stop(batches_processed, command.max_batches):
                    break
            return SyncIngestionResult(
                run_id="dry-run",
                records_upserted=total_upserted,
                records_rejected=total_rejected,
                batches_processed=batches_processed,
                years_processed=tuple(years_touched),
                rejected_territorial_codes=tuple(sorted(rejected_codes)),
            )

        run_id = self._repository.begin_run(command.source_id)
        try:
            for year in years:
                year_had_data = False
                for territorial_code in territorial_codes:
                    offset = 0
                    while True:
                        batch = self._fetch_batch(command, year, territorial_code, offset)
                        if not batch:
                            break

                        validated, summary = self._validate(command, batch)
                        total_rejected += summary.rejected_count
                        rejected_codes.update(summary.rejected_territorial_codes)

                        if validated:
                            total_upserted += self._repository.upsert_observations(
                                run_id=run_id,
                                source_id=command.source_id,
                                definition_id=command.definition_id,
                                records=validated,
                            )
                            year_had_data = True

                        batches_processed += 1
                        if progress and validated:
                            progress(
                                f"  year={year} muni={territorial_code} "
                                f"batch={batches_processed} upserted={len(validated)} "
                                f"total={total_upserted}",
                            )
                        if len(batch) < command.batch_size:
                            break
                        offset += len(batch)
                        if _should_stop(batches_processed, command.max_batches):
                            break
                    if _should_stop(batches_processed, command.max_batches):
                        break
                if year_had_data:
                    years_touched.append(year)
                if _should_stop(batches_processed, command.max_batches):
                    break

            self._repository.complete_run(run_id, records_upserted=total_upserted)
        except Exception as exc:
            self._repository.fail_run(run_id, str(exc))
            raise

        return SyncIngestionResult(
            run_id=run_id,
            records_upserted=total_upserted,
            records_rejected=total_rejected,
            batches_processed=batches_processed,
            years_processed=tuple(years_touched),
            rejected_territorial_codes=tuple(sorted(rejected_codes)),
        )

    def _fetch_batch(
        self,
        command: SyncIngestHealthIndicatorsCommand,
        year: int,
        territorial_code: str | None,
        offset: int,
    ) -> list[RawHealthIndicatorRecord]:
        if command.sync_strategy == "per_municipality" and territorial_code is None:
            return []
        return self._source_client.fetch_records(
            year=year,
            territorial_code=territorial_code,
            limit=command.batch_size,
            offset=offset,
        )

    def _validate(
        self,
        command: SyncIngestHealthIndicatorsCommand,
        records: list[RawHealthIndicatorRecord],
    ) -> tuple[list[RawHealthIndicatorRecord], TerritorialValidationSummary]:
        if not command.validate_territorial_codes or self._territorial_catalog is None:
            return records, TerritorialValidationSummary(
                accepted_count=len(records),
                rejected_count=0,
                rejected_territorial_codes=(),
            )
        return partition_records_by_catalog(records, self._territorial_catalog)


def resolve_sync_years(start_year: int | None, end_year: int) -> tuple[int, ...]:
    current_year = datetime.now(tz=UTC).year
    start = start_year if start_year is not None else current_year
    if start < end_year:
        start, end_year = end_year, start
    return tuple(range(start, end_year - 1, -1))


def _resolve_territorial_iterations(
    command: SyncIngestHealthIndicatorsCommand,
    catalog: TerritorialCatalog | None,
) -> tuple[str | None, ...]:
    if command.sync_strategy != "per_municipality":
        return (None,)
    if command.territorial_codes is not None:
        return command.territorial_codes
    if catalog is not None and hasattr(catalog, "all_municipality_codes"):
        return catalog.all_municipality_codes()
    return FEATURED_MUNICIPALITY_CODES


def _should_stop(batches_processed: int, max_batches: int | None) -> bool:
    return max_batches is not None and batches_processed >= max_batches
