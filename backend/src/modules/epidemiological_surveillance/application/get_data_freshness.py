from sqlalchemy import func, select
from sqlalchemy.orm import Session

from modules.epidemiological_surveillance.application.dto import DataFreshnessReadDto
from modules.epidemiological_surveillance.infrastructure.persistence.orm_models import (
    DataSourceRow,
    HealthIndicatorObservationRow,
    IngestionRunRow,
    IngestionRunStatus,
)


class GetDataFreshnessUseCase:
    """Returns lineage metadata for the latest successful ingestion."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def execute(self, source_id: str = "datos-gov-mortality-indicators") -> DataFreshnessReadDto:
        source = self._session.get(DataSourceRow, source_id)
        source_name = source.name if source is not None else source_id

        latest_run = self._session.scalars(
            select(IngestionRunRow)
            .where(
                IngestionRunRow.source_id == source_id,
                IngestionRunRow.status == IngestionRunStatus.SUCCEEDED.value,
            )
            .order_by(IngestionRunRow.finished_at.desc())
            .limit(1),
        ).first()

        latest_period = self._session.scalar(
            select(func.max(HealthIndicatorObservationRow.period)).where(
                HealthIndicatorObservationRow.definition_id == "general-mortality-rate",
            ),
        )

        return DataFreshnessReadDto(
            source_id=source_id,
            source_name=source_name,
            last_successful_ingestion_at=(
                latest_run.finished_at if latest_run is not None else None
            ),
            records_upserted=(
                latest_run.records_upserted if latest_run is not None else None
            ),
            latest_period_available=latest_period,
        )
