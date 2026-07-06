import uuid
from decimal import Decimal

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from modules.epidemiological_surveillance.application.normalization import observation_id
from modules.epidemiological_surveillance.domain.records import (
    RawHealthIndicatorRecord,
    RawMortalityIndicatorRecord,
)
from modules.epidemiological_surveillance.infrastructure.persistence.orm_models import (
    HealthIndicatorObservationRow,
    IngestionRunRow,
    IngestionRunStatus,
    utc_now,
)


def _serialize_int_tuple(values: tuple[int, ...]) -> str | None:
    if not values:
        return None
    return ",".join(str(value) for value in values)


def _serialize_str_tuple(values: tuple[str, ...]) -> str | None:
    if not values:
        return None
    return ",".join(values)


class SqlAlchemyIngestionRepository:
    """Persistence adapter for ingestion runs and curated observations."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def begin_run(self, source_id: str, *, sync_mode: str | None = None) -> str:
        run_id = uuid.uuid4().hex
        self._session.add(
            IngestionRunRow(
                id=run_id,
                source_id=source_id,
                status=IngestionRunStatus.RUNNING.value,
                started_at=utc_now(),
                records_upserted=0,
                records_rejected=0,
                sync_mode=sync_mode,
            )
        )
        self._session.commit()
        return run_id

    def complete_run(
        self,
        run_id: str,
        *,
        records_upserted: int,
        records_rejected: int = 0,
        batches_processed: int | None = None,
        years_processed: tuple[int, ...] = (),
        territorial_codes: tuple[str, ...] = (),
        sync_mode: str | None = None,
        bindings_used: tuple[str, ...] = (),
    ) -> None:
        run = self._session.get(IngestionRunRow, run_id)
        if run is None:
            msg = f"Ingestion run not found: {run_id}"
            raise RuntimeError(msg)
        run.status = IngestionRunStatus.SUCCEEDED.value
        run.finished_at = utc_now()
        run.records_upserted = records_upserted
        run.records_rejected = records_rejected
        run.batches_processed = batches_processed
        run.years_processed = _serialize_int_tuple(years_processed)
        run.territorial_codes = _serialize_str_tuple(territorial_codes)
        if sync_mode is not None:
            run.sync_mode = sync_mode
        run.bindings_used = _serialize_str_tuple(bindings_used)
        self._session.commit()

    def fail_run(self, run_id: str, error_message: str) -> None:
        run = self._session.get(IngestionRunRow, run_id)
        if run is None:
            return
        run.status = IngestionRunStatus.FAILED.value
        run.finished_at = utc_now()
        run.error_message = error_message[:2000]
        self._session.commit()

    def upsert_observations(
        self,
        *,
        run_id: str,
        source_id: str,
        definition_id: str,
        records: list[RawHealthIndicatorRecord | RawMortalityIndicatorRecord],
    ) -> int:
        del source_id
        if not records:
            return 0

        normalized_records = [
            record.to_health_record() if isinstance(record, RawMortalityIndicatorRecord) else record
            for record in records
        ]

        rows = [
            {
                "id": observation_id(
                    definition_id,
                    record.territorial_code,
                    record.period,
                ),
                "definition_id": definition_id,
                "territorial_code": record.territorial_code,
                "period": record.period,
                "value": Decimal(record.value),
                "ingestion_run_id": run_id,
            }
            for record in normalized_records
        ]

        batch_size = 1000
        for offset in range(0, len(rows), batch_size):
            batch = rows[offset : offset + batch_size]
            stmt = insert(HealthIndicatorObservationRow).values(batch)
            stmt = stmt.on_conflict_do_update(
                index_elements=["definition_id", "territorial_code", "period"],
                set_={
                    "value": stmt.excluded.value,
                    "ingestion_run_id": stmt.excluded.ingestion_run_id,
                },
            )
            self._session.execute(stmt)
        self._session.commit()
        return len(rows)
