from decimal import Decimal
from typing import Protocol

from modules.territorial_risk.domain.risk_score import MortalityObservation


class TerritorialRiskDataPort(Protocol):
    def get_mortality_observation(
        self,
        territorial_code: str,
        period: str,
    ) -> MortalityObservation | None:
        """Return curated general mortality for a territory and period."""

    def get_national_median_mortality(self, period: str) -> Decimal | None:
        """Return national median general mortality for the given period."""
