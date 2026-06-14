from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from modules.anomaly_detection.domain.detection import ObservationWithBaseline
from modules.anomaly_detection.domain.repositories import (
    TerritorialSeriesPoint,
)
from modules.epidemiological_surveillance.infrastructure.persistence.orm_models import (
    HealthIndicatorDefinitionRow,
    HealthIndicatorObservationRow,
)


class SqlAlchemyCuratedObservationsReader:
    """Shared read access to curated indicator observations."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def list_observations_with_period_median(
        self,
        definition_id: str,
        *,
        territorial_code: str | None = None,
    ) -> list[ObservationWithBaseline]:
        median_subquery = (
            select(
                HealthIndicatorObservationRow.period.label("median_period"),
                func.percentile_cont(0.5)
                .within_group(HealthIndicatorObservationRow.value)
                .label("baseline"),
            )
            .join(
                HealthIndicatorDefinitionRow,
                HealthIndicatorObservationRow.definition_id == HealthIndicatorDefinitionRow.id,
            )
            .where(HealthIndicatorDefinitionRow.id == definition_id)
            .group_by(HealthIndicatorObservationRow.period)
            .subquery()
        )

        stmt = (
            select(
                HealthIndicatorObservationRow.territorial_code,
                HealthIndicatorObservationRow.period,
                HealthIndicatorObservationRow.value,
                median_subquery.c.baseline,
                HealthIndicatorDefinitionRow.id,
                HealthIndicatorDefinitionRow.name,
            )
            .join(
                HealthIndicatorDefinitionRow,
                HealthIndicatorObservationRow.definition_id == HealthIndicatorDefinitionRow.id,
            )
            .join(
                median_subquery,
                HealthIndicatorObservationRow.period == median_subquery.c.median_period,
            )
            .where(HealthIndicatorDefinitionRow.id == definition_id)
            .order_by(
                HealthIndicatorObservationRow.period.desc(),
                HealthIndicatorObservationRow.territorial_code,
            )
        )
        if territorial_code is not None:
            stmt = stmt.where(HealthIndicatorObservationRow.territorial_code == territorial_code)

        rows = self._session.execute(stmt).all()
        return [
            ObservationWithBaseline(
                territorial_code=row.territorial_code,
                period=row.period,
                value=Decimal(row.value),
                baseline=Decimal(row.baseline),
                definition_id=row.id,
                definition_name=row.name,
            )
            for row in rows
        ]

    def list_territorial_series(
        self,
        territorial_code: str,
        definition_id: str,
    ) -> tuple[str, list[TerritorialSeriesPoint]]:
        stmt = (
            select(
                HealthIndicatorObservationRow.period,
                HealthIndicatorObservationRow.value,
                HealthIndicatorDefinitionRow.name,
            )
            .join(
                HealthIndicatorDefinitionRow,
                HealthIndicatorObservationRow.definition_id == HealthIndicatorDefinitionRow.id,
            )
            .where(
                HealthIndicatorDefinitionRow.id == definition_id,
                HealthIndicatorObservationRow.territorial_code == territorial_code,
            )
            .order_by(HealthIndicatorObservationRow.period.asc())
        )
        rows = self._session.execute(stmt).all()
        if not rows:
            return definition_id, []

        return rows[0].name, [
            TerritorialSeriesPoint(period=row.period, value=Decimal(row.value)) for row in rows
        ]
