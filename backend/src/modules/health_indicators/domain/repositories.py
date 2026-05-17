from typing import Protocol

from modules.health_indicators.domain.health_indicator import HealthIndicator


class HealthIndicatorRepository(Protocol):
    def list_all(self) -> list[HealthIndicator]:
        """Return all health indicator definitions available to the application."""
