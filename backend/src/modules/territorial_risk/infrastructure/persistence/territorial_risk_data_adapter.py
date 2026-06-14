from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from modules.epidemiological_surveillance.infrastructure.persistence.orm_models import (
    HealthIndicatorDefinitionRow,
    HealthIndicatorObservationRow,
)
from modules.territorial_risk.domain.risk_score import (
    GENERAL_MORTALITY_DEFINITION_ID,
    MortalityObservation,
)


class SqlAlchemyTerritorialRiskDataAdapter:
    """Reads curated indicator observations for territorial risk scoring."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_mortality_observation(
        self,
        territorial_code: str,
        period: str,
    ) -> MortalityObservation | None:
        stmt = (
            select(HealthIndicatorObservationRow)
            .join(
                HealthIndicatorDefinitionRow,
                HealthIndicatorObservationRow.definition_id == HealthIndicatorDefinitionRow.id,
            )
            .where(
                HealthIndicatorDefinitionRow.id == GENERAL_MORTALITY_DEFINITION_ID,
                HealthIndicatorObservationRow.territorial_code == territorial_code,
                HealthIndicatorObservationRow.period == period,
            )
            .limit(1)
        )
        row = self._session.scalars(stmt).first()
        if row is None:
            return None
        return MortalityObservation(
            definition_id=row.definition_id,
            territorial_code=row.territorial_code,
            period=row.period,
            value=Decimal(row.value),
        )

    def get_national_median_mortality(self, period: str) -> Decimal | None:
        stmt = (
            select(
                func.percentile_cont(0.5)
                .within_group(HealthIndicatorObservationRow.value)
                .label("median_value"),
            )
            .select_from(HealthIndicatorObservationRow)
            .join(
                HealthIndicatorDefinitionRow,
                HealthIndicatorObservationRow.definition_id == HealthIndicatorDefinitionRow.id,
            )
            .where(
                HealthIndicatorDefinitionRow.id == GENERAL_MORTALITY_DEFINITION_ID,
                HealthIndicatorObservationRow.period == period,
            )
        )
        median_value = self._session.scalar(stmt)
        if median_value is None:
            return None
        return Decimal(median_value)

    def list_territorial_codes_for_period(
        self,
        period: str,
        *,
        definition_id: str = GENERAL_MORTALITY_DEFINITION_ID,
        limit: int = 500,
    ) -> list[str]:
        stmt = (
            select(HealthIndicatorObservationRow.territorial_code)
            .where(
                HealthIndicatorObservationRow.definition_id == definition_id,
                HealthIndicatorObservationRow.period == period,
            )
            .order_by(HealthIndicatorObservationRow.territorial_code)
            .limit(limit)
        )
        return list(self._session.scalars(stmt).all())
