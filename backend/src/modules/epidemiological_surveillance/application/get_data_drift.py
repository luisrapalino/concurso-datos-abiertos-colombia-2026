from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from modules.epidemiological_surveillance.application.dto import DataDriftReadDto
from modules.epidemiological_surveillance.infrastructure.persistence.orm_models import (
    HealthIndicatorObservationRow,
)


class GetDataDriftUseCase:
    """Detects basic distribution drift between the latest curated periods."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def execute(
        self,
        source_id: str = "datos-gov-mortality-indicators",
        definition_id: str = "general-mortality-rate",
    ) -> DataDriftReadDto:
        del source_id
        periods = list(
            self._session.scalars(
                select(HealthIndicatorObservationRow.period)
                .where(HealthIndicatorObservationRow.definition_id == definition_id)
                .distinct()
                .order_by(HealthIndicatorObservationRow.period.desc()),
            ).all(),
        )
        if not periods:
            return DataDriftReadDto(
                definition_id=definition_id,
                latest_period=None,
                previous_period=None,
                latest_observation_count=0,
                previous_observation_count=0,
                observation_count_delta=0,
                latest_mean_value=None,
                previous_mean_value=None,
                mean_value_delta=None,
                drift_status="unknown",
                drift_note="No curated observations available for drift analysis.",
            )

        latest_period = periods[0]
        previous_period = periods[1] if len(periods) > 1 else None
        latest_stats = self._period_stats(definition_id, latest_period)
        previous_stats = (
            self._period_stats(definition_id, previous_period)
            if previous_period is not None
            else (0, None)
        )

        count_delta = latest_stats[0] - previous_stats[0]
        mean_delta = None
        if latest_stats[1] is not None and previous_stats[1] is not None:
            mean_delta = float(latest_stats[1] - previous_stats[1])

        drift_status, drift_note = _classify_drift(
            count_delta=count_delta,
            mean_delta=mean_delta,
            has_previous=previous_period is not None,
        )

        return DataDriftReadDto(
            definition_id=definition_id,
            latest_period=latest_period,
            previous_period=previous_period,
            latest_observation_count=latest_stats[0],
            previous_observation_count=previous_stats[0],
            observation_count_delta=count_delta,
            latest_mean_value=float(latest_stats[1]) if latest_stats[1] is not None else None,
            previous_mean_value=float(previous_stats[1]) if previous_stats[1] is not None else None,
            mean_value_delta=mean_delta,
            drift_status=drift_status,
            drift_note=drift_note,
        )

    def _period_stats(
        self,
        definition_id: str,
        period: str,
    ) -> tuple[int, Decimal | None]:
        count = self._session.scalar(
            select(func.count())
            .select_from(HealthIndicatorObservationRow)
            .where(
                HealthIndicatorObservationRow.definition_id == definition_id,
                HealthIndicatorObservationRow.period == period,
            ),
        )
        mean_value = self._session.scalar(
            select(func.avg(HealthIndicatorObservationRow.value)).where(
                HealthIndicatorObservationRow.definition_id == definition_id,
                HealthIndicatorObservationRow.period == period,
            ),
        )
        return int(count or 0), mean_value


def _classify_drift(
    *,
    count_delta: int,
    mean_delta: float | None,
    has_previous: bool,
) -> tuple[str, str]:
    if not has_previous:
        return "stable", "Single period available; drift analysis requires at least two periods."

    abs_mean_delta = abs(mean_delta or 0.0)
    if abs(count_delta) > 50 or abs_mean_delta > 0.75:
        return (
            "alert",
            "Significant change detected in observation volume or mean mortality between periods.",
        )
    if abs(count_delta) > 10 or abs_mean_delta > 0.25:
        return (
            "warning",
            "Moderate change detected between latest periods; review ingestion and source updates.",
        )
    return "stable", "Latest periods remain within expected MVP drift thresholds."
