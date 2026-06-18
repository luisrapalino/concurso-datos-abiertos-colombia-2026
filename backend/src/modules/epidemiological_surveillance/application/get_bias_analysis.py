from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from modules.epidemiological_surveillance.application.bias_dto import (
    BiasAnalysisReadDto,
    DepartmentMortalitySummaryDto,
)
from modules.epidemiological_surveillance.infrastructure.persistence.orm_models import (
    HealthIndicatorObservationRow,
)


class GetBiasAnalysisUseCase:
    """Summarizes mortality distribution by department for equity review."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def execute(
        self,
        *,
        period: str,
        definition_id: str = "general-mortality-rate",
    ) -> BiasAnalysisReadDto:
        rows = self._session.execute(
            select(
                HealthIndicatorObservationRow.territorial_code,
                func.count().label("count"),
                func.avg(HealthIndicatorObservationRow.value).label("mean_value"),
            )
            .where(
                HealthIndicatorObservationRow.definition_id == definition_id,
                HealthIndicatorObservationRow.period == period,
            )
            .group_by(HealthIndicatorObservationRow.territorial_code),
        ).all()

        department_stats: dict[str, list[tuple[int, Decimal]]] = {}
        for territorial_code, count, mean_value in rows:
            department_code = str(territorial_code)[:2]
            department_stats.setdefault(department_code, []).append((int(count), mean_value))

        departments: list[DepartmentMortalitySummaryDto] = []
        total_weighted = Decimal("0")
        total_count = 0
        for department_code, values in sorted(department_stats.items()):
            obs_count = sum(item[0] for item in values)
            weighted_sum = sum(Decimal(item[0]) * Decimal(item[1]) for item in values)
            mean_mortality = float(weighted_sum / obs_count) if obs_count else 0.0
            departments.append(
                DepartmentMortalitySummaryDto(
                    department_code=department_code,
                    department_name=f"Departamento {department_code}",
                    observation_count=obs_count,
                    mean_mortality=round(mean_mortality, 4),
                ),
            )
            total_weighted += weighted_sum
            total_count += obs_count

        national_mean = float(total_weighted / total_count) if total_count else 0.0
        return BiasAnalysisReadDto(
            definition_id=definition_id,
            period=period,
            national_mean=round(national_mean, 4),
            departments=departments,
        )
