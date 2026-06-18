from sqlalchemy import func, select
from sqlalchemy.orm import Session

from modules.epidemiological_surveillance.application.dto import DataFreshnessReadDto
from modules.epidemiological_surveillance.infrastructure.persistence.orm_models import (
    DataSourceRow,
    HealthIndicatorObservationRow,
    IngestionRunRow,
    IngestionRunStatus,
)
from shared.sivigila_events import sivigila_definition_ids

SOURCE_DEFINITION_MAP: dict[str, str] = {
    "datos-gov-mortality-indicators": "general-mortality-rate",
    "datos-gov-vaccination-coverage": "dpta-penta-vaccination-coverage",
    "datos-gov-air-quality": "pm25-annual-mean",
}


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

        if source_id == "datos-gov-sivigila":
            definition_ids = sivigila_definition_ids()
            latest_period = self._session.scalar(
                select(func.max(HealthIndicatorObservationRow.period)).where(
                    HealthIndicatorObservationRow.definition_id.in_(definition_ids),
                ),
            )
            records_upserted = self._session.scalar(
                select(func.count()).where(
                    HealthIndicatorObservationRow.definition_id.in_(definition_ids),
                ),
            )
        else:
            definition_id = SOURCE_DEFINITION_MAP.get(source_id, "general-mortality-rate")
            latest_period = self._session.scalar(
                select(func.max(HealthIndicatorObservationRow.period)).where(
                    HealthIndicatorObservationRow.definition_id == definition_id,
                ),
            )
            records_upserted = latest_run.records_upserted if latest_run is not None else None

        return DataFreshnessReadDto(
            source_id=source_id,
            source_name=source_name,
            last_successful_ingestion_at=(
                latest_run.finished_at if latest_run is not None else None
            ),
            records_upserted=records_upserted,
            latest_period_available=latest_period,
        )
