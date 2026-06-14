from modules.epidemiological_surveillance.application.normalization import (
    IngestMortalityIndicatorsCommand,
)
from modules.epidemiological_surveillance.domain.records import RawMortalityIndicatorRecord
from modules.epidemiological_surveillance.domain.repositories import (
    IngestionRepository,
    IngestionResult,
    MortalityIndicatorsSourceClient,
)


class IngestMortalityIndicatorsUseCase:
    """Batch ingestion of curated mortality indicators from datos.gov.co."""

    def __init__(
        self,
        source_client: MortalityIndicatorsSourceClient,
        repository: IngestionRepository,
    ) -> None:
        self._source_client = source_client
        self._repository = repository

    def execute(self, command: IngestMortalityIndicatorsCommand) -> IngestionResult:
        if command.dry_run:
            records = self._fetch_all(command)
            return IngestionResult(run_id="dry-run", records_upserted=len(records))

        run_id = self._repository.begin_run(command.source_id)
        try:
            records = self._fetch_all(command)
            upserted = self._repository.upsert_observations(
                run_id=run_id,
                source_id=command.source_id,
                definition_id=command.definition_id,
                records=records,
            )
            self._repository.complete_run(run_id, records_upserted=upserted)
        except Exception as exc:
            self._repository.fail_run(run_id, str(exc))
            raise

        return IngestionResult(run_id=run_id, records_upserted=upserted)

    def _fetch_all(
        self,
        command: IngestMortalityIndicatorsCommand,
    ) -> list[RawMortalityIndicatorRecord]:
        target_years = _resolve_target_years(command)
        if len(target_years) == 1:
            return self._fetch_for_year(command, target_years[0])

        per_year_limit = max(command.limit // len(target_years), 1)
        collected: list[RawMortalityIndicatorRecord] = []
        for year in target_years:
            if len(collected) >= command.limit:
                break
            remaining = command.limit - len(collected)
            collected.extend(
                self._fetch_for_year(
                    command,
                    year,
                    limit=min(per_year_limit, remaining),
                ),
            )
        return collected

    def _fetch_for_year(
        self,
        command: IngestMortalityIndicatorsCommand,
        year: int | None,
        *,
        limit: int | None = None,
    ) -> list[RawMortalityIndicatorRecord]:
        max_records = limit if limit is not None else command.limit
        collected: list[RawMortalityIndicatorRecord] = []
        offset = 0
        batch_size = min(max_records, 5000)

        while len(collected) < max_records:
            batch = self._source_client.fetch_general_mortality_records(
                year=year,
                limit=min(batch_size, max_records - len(collected)),
                offset=offset,
            )
            if not batch:
                break
            collected.extend(batch)
            if len(batch) < batch_size:
                break
            offset += len(batch)

        return collected


def _resolve_target_years(command: IngestMortalityIndicatorsCommand) -> tuple[int | None, ...]:
    if command.years:
        return command.years
    if command.year is not None:
        return (command.year,)
    return (None,)
