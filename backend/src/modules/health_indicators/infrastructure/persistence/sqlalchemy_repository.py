from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.health_indicators.domain.health_indicator import HealthIndicator
from modules.health_indicators.infrastructure.persistence.orm_models import HealthIndicatorRow


def _row_to_domain(row: HealthIndicatorRow) -> HealthIndicator:
    return HealthIndicator(
        id=row.id,
        name=row.name,
        territorial_code=row.territorial_code,
        measurement_unit=row.measurement_unit,
    )


class SqlAlchemyHealthIndicatorRepository:
    """Persistence adapter for health indicator definitions."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def list_all(self) -> list[HealthIndicator]:
        stmt = select(HealthIndicatorRow).order_by(HealthIndicatorRow.id)
        rows = list(self._session.scalars(stmt).all())
        return [_row_to_domain(row) for row in rows]
