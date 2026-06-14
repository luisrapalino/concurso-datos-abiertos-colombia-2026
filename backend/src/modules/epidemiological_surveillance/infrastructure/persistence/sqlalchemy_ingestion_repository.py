import uuid
from decimal import Decimal

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from modules.epidemiological_surveillance.application.normalization import (
    annual_period,
    observation_id,
)
from modules.epidemiological_surveillance.domain.records import RawMortalityIndicatorRecord
from modules.epidemiological_surveillance.infrastructure.persistence.orm_models import (
    HealthIndicatorObservationRow,
    IngestionRunRow,
    IngestionRunStatus,
    utc_now,
)


class SqlAlchemyIngestionRepository:
    """Persistence adapter for ingestion runs and curated observations."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def begin_run(self, source_id: str) -> str:
        run_id = uuid.uuid4().hex
        self._session.add(
            IngestionRunRow(
                id=run_id,
                source_id=source_id,
                status=IngestionRunStatus.RUNNING.value,
                started_at=utc_now(),
                records_upserted=0,
            )
        )
        self._session.commit()
        return run_id

    def complete_run(self, run_id: str, *, records_upserted: int) -> None:
        run = self._session.get(IngestionRunRow, run_id)
        if run is None:
            msg = f"Ingestion run not found: {run_id}"
            raise RuntimeError(msg)
        run.status = IngestionRunStatus.SUCCEEDED.value
        run.finished_at = utc_now()
        run.records_upserted = records_upserted
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
        records: list[RawMortalityIndicatorRecord],
    ) -> int:
        del source_id
        if not records:
            return 0

        rows = [
            {
                "id": observation_id(
                    definition_id,
                    record.territorial_code,
                    annual_period(record.year),
                ),
                "definition_id": definition_id,
                "territorial_code": record.territorial_code,
                "period": annual_period(record.year),
                "value": Decimal(record.value),
                "ingestion_run_id": run_id,
            }
            for record in records
        ]

        stmt = insert(HealthIndicatorObservationRow).values(rows)
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
