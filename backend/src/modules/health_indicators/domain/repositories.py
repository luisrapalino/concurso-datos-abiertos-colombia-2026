from dataclasses import dataclass
from typing import Protocol

from modules.health_indicators.domain.health_indicator import HealthIndicator


@dataclass(frozen=True, slots=True)
class ListHealthIndicatorsQuery:
    territorial_code: str | None = None
    period: str | None = None
    definition_id: str | None = None
    limit: int = 100


class HealthIndicatorRepository(Protocol):
    def list_observations(self, query: ListHealthIndicatorsQuery) -> list[HealthIndicator]:
        """Return curated health indicator observations matching the query."""
