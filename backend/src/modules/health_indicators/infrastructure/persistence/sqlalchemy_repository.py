from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.epidemiological_surveillance.infrastructure.persistence.orm_models import (
    HealthIndicatorDefinitionRow,
    HealthIndicatorObservationRow,
    IngestionRunRow,
)
from modules.health_indicators.domain.health_indicator import HealthIndicator
from modules.health_indicators.domain.repositories import ListHealthIndicatorsQuery


def _row_to_domain(
    observation: HealthIndicatorObservationRow,
    definition: HealthIndicatorDefinitionRow,
    ingestion_run: IngestionRunRow | None,
) -> HealthIndicator:
    return HealthIndicator(
        id=observation.id,
        definition_id=definition.id,
        name=definition.name,
        territorial_code=observation.territorial_code,
        period=observation.period,
        value=observation.value,
        measurement_unit=definition.measurement_unit,
        source_id=definition.source_id,
        ingested_at=ingestion_run.finished_at if ingestion_run else None,
    )


class SqlAlchemyHealthIndicatorRepository:
    """Read adapter for curated health indicator observations."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def list_observations(self, query: ListHealthIndicatorsQuery) -> list[HealthIndicator]:
        stmt = (
            select(
                HealthIndicatorObservationRow,
                HealthIndicatorDefinitionRow,
                IngestionRunRow,
            )
            .join(
                HealthIndicatorDefinitionRow,
                HealthIndicatorObservationRow.definition_id == HealthIndicatorDefinitionRow.id,
            )
            .join(
                IngestionRunRow,
                HealthIndicatorObservationRow.ingestion_run_id == IngestionRunRow.id,
            )
            .order_by(
                HealthIndicatorObservationRow.period.desc(),
                HealthIndicatorObservationRow.territorial_code,
            )
            .limit(query.limit)
        )

        if query.territorial_code is not None:
            stmt = stmt.where(
                HealthIndicatorObservationRow.territorial_code == query.territorial_code,
            )
        if query.period is not None:
            stmt = stmt.where(HealthIndicatorObservationRow.period == query.period)
        if query.definition_id is not None:
            stmt = stmt.where(HealthIndicatorDefinitionRow.id == query.definition_id)

        rows = self._session.execute(stmt).all()
        return [
            _row_to_domain(observation, definition, run)
            for observation, definition, run in rows
        ]
