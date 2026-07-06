from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass

from modules.epidemiological_surveillance.application.municipal_dataset_resolver import (
    MunicipalDatasetResolver,
)
from modules.epidemiological_surveillance.application.sync_ingest_health_indicators import (
    resolve_sync_years,
)
from modules.epidemiological_surveillance.application.validate_territorial_records import (
    partition_records_by_catalog,
)
from modules.epidemiological_surveillance.domain.repositories import (
    IngestionRepository,
    SyncIngestionResult,
)
from shared.divipola_catalog import TerritorialCatalog
from shared.featured_municipalities import FEATURED_MUNICIPALITY_CODES
from shared.municipal_dataset_catalog import COMPETITION_DEFINITION_IDS, MunicipalDatasetBinding


@dataclass(frozen=True, slots=True)
class SyncMunicipalIndicatorsCommand:
    territorial_codes: tuple[str, ...]
    definition_ids: tuple[str, ...]
    batch_size: int
    start_year: int | None
    end_year: int
    dry_run: bool = False
    validate_territorial_codes: bool = True
    max_batches: int | None = None


class SyncMunicipalIndicatorsUseCase:
    """Ingests indicators municipality-by-municipality, picking the best dataset per variable."""

    def __init__(
        self,
        resolver: MunicipalDatasetResolver,
        repository: IngestionRepository,
        *,
        territorial_catalog: TerritorialCatalog | None = None,
    ) -> None:
        self._resolver = resolver
        self._repository = repository
        self._territorial_catalog = territorial_catalog

    def execute(
        self,
        command: SyncMunicipalIndicatorsCommand,
        *,
        progress: Callable[[str], None] | None = None,
    ) -> SyncIngestionResult:
        years = resolve_sync_years(command.start_year, command.end_year)
        batches_processed = 0
        total_upserted = 0
        total_rejected = 0
        rejected_codes: set[str] = set()
        years_touched: list[int] = []
        runs_by_source: dict[str, str] = {}
        upserted_by_source: dict[str, int] = defaultdict(int)
        rejected_by_source: dict[str, int] = defaultdict(int)
        bindings_by_source: dict[str, set[str]] = defaultdict(set)

        try:
            for territorial_code in command.territorial_codes:
                for definition_id in command.definition_ids:
                    for year in years:
                        locked_binding: MunicipalDatasetBinding | None = None
                        offset = 0
                        year_had_data = False

                        while True:
                            resolution = self._resolver.resolve_page(
                                definition_id=definition_id,
                                territorial_code=territorial_code,
                                year=year,
                                limit=command.batch_size,
                                offset=offset,
                                locked_binding=locked_binding,
                            )
                            if resolution is None:
                                break

                            locked_binding = resolution.binding
                            bindings_by_source[resolution.binding.source_id].add(
                                resolution.binding.binding_id,
                            )
                            if not resolution.records:
                                break

                            validated = resolution.records
                            if (
                                command.validate_territorial_codes
                                and self._territorial_catalog is not None
                            ):
                                validated, summary = partition_records_by_catalog(
                                    resolution.records,
                                    self._territorial_catalog,
                                )
                                total_rejected += summary.rejected_count
                                rejected_by_source[resolution.binding.source_id] += summary.rejected_count
                                rejected_codes.update(summary.rejected_territorial_codes)

                            if validated:
                                total_upserted += len(validated)
                                year_had_data = True
                                if not command.dry_run:
                                    source_id = resolution.binding.source_id
                                    if source_id not in runs_by_source:
                                        runs_by_source[source_id] = self._repository.begin_run(
                                            source_id,
                                            sync_mode="municipal",
                                        )
                                    upserted = self._repository.upsert_observations(
                                        run_id=runs_by_source[source_id],
                                        source_id=source_id,
                                        definition_id=definition_id,
                                        records=validated,
                                    )
                                    upserted_by_source[source_id] += upserted

                            batches_processed += 1
                            if progress and validated:
                                progress(
                                    f"  muni={territorial_code} var={definition_id} "
                                    f"dataset={resolution.binding.binding_id} year={year} "
                                    f"batch={batches_processed} upserted={len(validated)} "
                                    f"total={total_upserted}",
                                )

                            if len(resolution.records) < command.batch_size:
                                break
                            offset += len(resolution.records)
                            if _should_stop(batches_processed, command.max_batches):
                                break

                        if year_had_data and year not in years_touched:
                            years_touched.append(year)
                        if _should_stop(batches_processed, command.max_batches):
                            break
                    if _should_stop(batches_processed, command.max_batches):
                        break
                if _should_stop(batches_processed, command.max_batches):
                    break
        except Exception as exc:
            for run_id in runs_by_source.values():
                self._repository.fail_run(run_id, str(exc))
            raise

        if not command.dry_run:
            for source_id, run_id in runs_by_source.items():
                self._repository.complete_run(
                    run_id,
                    records_upserted=upserted_by_source[source_id],
                    records_rejected=rejected_by_source[source_id],
                    batches_processed=batches_processed,
                    years_processed=tuple(years_touched),
                    territorial_codes=command.territorial_codes,
                    sync_mode="municipal",
                    bindings_used=tuple(sorted(bindings_by_source[source_id])),
                )

        return SyncIngestionResult(
            run_id=next(iter(runs_by_source.values()), "dry-run" if command.dry_run else "noop"),
            records_upserted=total_upserted,
            records_rejected=total_rejected,
            batches_processed=batches_processed,
            years_processed=tuple(years_touched),
            rejected_territorial_codes=tuple(sorted(rejected_codes)),
        )


def _should_stop(batches_processed: int, max_batches: int | None) -> bool:
    return max_batches is not None and batches_processed >= max_batches


def default_municipal_sync_command(
    *,
    territorial_codes: tuple[str, ...] | None,
    definition_ids: tuple[str, ...] | None,
    batch_size: int,
    start_year: int | None,
    end_year: int,
    dry_run: bool,
    validate_territorial_codes: bool,
    max_batches: int | None,
) -> SyncMunicipalIndicatorsCommand:
    return SyncMunicipalIndicatorsCommand(
        territorial_codes=territorial_codes or FEATURED_MUNICIPALITY_CODES,
        definition_ids=definition_ids or COMPETITION_DEFINITION_IDS,
        batch_size=batch_size,
        start_year=start_year,
        end_year=end_year,
        dry_run=dry_run,
        validate_territorial_codes=validate_territorial_codes,
        max_batches=max_batches,
    )
