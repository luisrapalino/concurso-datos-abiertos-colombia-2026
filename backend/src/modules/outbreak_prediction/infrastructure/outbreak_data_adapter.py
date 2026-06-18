
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from modules.epidemiological_surveillance.infrastructure.persistence.orm_models import (
    HealthIndicatorObservationRow,
)
from modules.outbreak_prediction.domain.outbreak_prediction import (
    HEALTH_ACCESS_DEFINITION_ID,
    PM25_DEFINITION_ID,
    VACCINATION_DEFINITION_ID,
)
from modules.outbreak_prediction.domain.repositories import OutbreakFeatureBundle
from shared.sivigila_events import resolve_sivigila_event


class SqlAlchemyOutbreakDataAdapter:
    """Loads multivariate outbreak features from curated observations."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_feature_bundle(
        self,
        territorial_code: str,
        period: str,
        *,
        event_code: str,
    ) -> OutbreakFeatureBundle | None:
        event = resolve_sivigila_event(event_code)
        if event is None:
            return None

        definition_id = event.definition_id
        observed = self._get_observation(definition_id, territorial_code, period)
        if observed is None:
            return None

        baseline = self._session.scalar(
            select(func.percentile_cont(0.5).within_group(HealthIndicatorObservationRow.value)).where(
                HealthIndicatorObservationRow.definition_id == definition_id,
                HealthIndicatorObservationRow.period == period,
            ),
        )
        if baseline is None:
            return None

        year = int(period[:4])
        annual_period = f"{year:04d}-01"
        previous_period = _previous_epidemiological_week(period)

        return OutbreakFeatureBundle(
            territorial_code=territorial_code,
            period=period,
            event_code=event.code,
            event_name=event.name,
            observed_cases=observed,
            baseline_cases=baseline,
            previous_week_cases=self._get_observation(
                definition_id,
                territorial_code,
                previous_period,
            ),
            vaccination_coverage_pct=self._get_observation(
                VACCINATION_DEFINITION_ID,
                territorial_code,
                annual_period,
            ),
            health_access_pct=self._get_observation(
                HEALTH_ACCESS_DEFINITION_ID,
                territorial_code,
                annual_period,
            ),
            pm25_ug_m3=self._get_observation(
                PM25_DEFINITION_ID,
                territorial_code,
                annual_period,
            ),
        )

    def list_territories_with_cases(
        self,
        period: str,
        *,
        event_code: str,
        limit: int = 100,
    ) -> list[str]:
        event = resolve_sivigila_event(event_code)
        if event is None:
            return []

        stmt = (
            select(HealthIndicatorObservationRow.territorial_code)
            .where(
                HealthIndicatorObservationRow.definition_id == event.definition_id,
                HealthIndicatorObservationRow.period == period,
            )
            .order_by(HealthIndicatorObservationRow.value.desc())
            .limit(limit)
        )
        return list(self._session.scalars(stmt).all())

    def _get_observation(
        self,
        definition_id: str,
        territorial_code: str,
        period: str,
    ):
        return self._session.scalar(
            select(HealthIndicatorObservationRow.value).where(
                HealthIndicatorObservationRow.definition_id == definition_id,
                HealthIndicatorObservationRow.territorial_code == territorial_code,
                HealthIndicatorObservationRow.period == period,
            ),
        )


def _previous_epidemiological_week(period: str) -> str:
    if "-W" not in period:
        return period
    year_str, week_str = period.split("-W", maxsplit=1)
    year = int(year_str)
    week = int(week_str)
    if week > 1:
        return f"{year:04d}-W{week - 1:02d}"
    return f"{year - 1:04d}-W52"
