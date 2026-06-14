from sqlalchemy import func, select
from sqlalchemy.orm import Session

from modules.epidemiological_surveillance.application.dto import DataQualityReadDto
from modules.epidemiological_surveillance.infrastructure.persistence.orm_models import (
    HealthIndicatorObservationRow,
    IngestionRunRow,
    IngestionRunStatus,
)


class GetDataQualityUseCase:
    """Summarizes curated dataset coverage for drift and quality monitoring."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def execute(
        self,
        source_id: str = "datos-gov-mortality-indicators",
        definition_id: str = "general-mortality-rate",
    ) -> DataQualityReadDto:

        total_observations = self._session.scalar(
            select(func.count())
            .select_from(HealthIndicatorObservationRow)
            .where(HealthIndicatorObservationRow.definition_id == definition_id),
        )
        distinct_territories = self._session.scalar(
            select(func.count(func.distinct(HealthIndicatorObservationRow.territorial_code)))
            .select_from(HealthIndicatorObservationRow)
            .where(HealthIndicatorObservationRow.definition_id == definition_id),
        )
        distinct_periods = self._session.scalar(
            select(func.count(func.distinct(HealthIndicatorObservationRow.period)))
            .select_from(HealthIndicatorObservationRow)
            .where(HealthIndicatorObservationRow.definition_id == definition_id),
        )
        periods_available = list(
            self._session.scalars(
                select(HealthIndicatorObservationRow.period)
                .where(HealthIndicatorObservationRow.definition_id == definition_id)
                .distinct()
                .order_by(HealthIndicatorObservationRow.period.asc()),
            ).all(),
        )
        latest_ingestion = self._session.scalars(
            select(IngestionRunRow.finished_at)
            .where(IngestionRunRow.status == IngestionRunStatus.SUCCEEDED.value)
            .order_by(IngestionRunRow.finished_at.desc())
            .limit(1),
        ).first()

        temporal_note = _temporal_coverage_note(distinct_periods or 0, periods_available)

        return DataQualityReadDto(
            source_id=source_id,
            total_observations=int(total_observations or 0),
            distinct_territories=int(distinct_territories or 0),
            distinct_periods=int(distinct_periods or 0),
            periods_available=periods_available,
            latest_ingestion_at=latest_ingestion,
            temporal_coverage_note=temporal_note,
        )


def _temporal_coverage_note(distinct_periods: int, periods_available: list[str]) -> str:
    if distinct_periods <= 1:
        return (
            "Cobertura temporal limitada: se recomienda ingestión multi-año "
            "antes de interpretar tendencias o proyecciones."
        )
    return (
        f"Panel temporal con {distinct_periods} periodos disponibles "
        f"({periods_available[0]} → {periods_available[-1]})."
    )
