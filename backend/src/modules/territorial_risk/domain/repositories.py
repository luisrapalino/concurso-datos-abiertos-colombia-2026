from decimal import Decimal
from typing import Protocol

from modules.territorial_risk.domain.risk_score import (
    GENERAL_MORTALITY_DEFINITION_ID,
    MortalityObservation,
    RiskScore,
)


class TerritorialRiskDataPort(Protocol):
    def get_mortality_observation(
        self,
        territorial_code: str,
        period: str,
    ) -> MortalityObservation | None:
        """Return curated general mortality for a territory and period."""

    def get_national_median_mortality(self, period: str) -> Decimal | None:
        """Return national median general mortality for the given period."""

    def list_territorial_codes_for_period(
        self,
        period: str,
        *,
        definition_id: str = GENERAL_MORTALITY_DEFINITION_ID,
        limit: int = 500,
    ) -> list[str]:
        """Return territorial codes with observations for map and batch scoring."""


class RiskScoreRepository(Protocol):
    def get(
        self,
        *,
        territorial_code: str,
        period: str,
        definition_id: str,
        model_version: str,
    ) -> RiskScore | None:
        """Return a persisted score when available."""

    def save(self, risk_score: RiskScore) -> None:
        """Persist or update a computed territorial risk score."""

    def list_for_period(
        self,
        *,
        period: str,
        definition_id: str,
        model_version: str,
        limit: int = 500,
    ) -> list[RiskScore]:
        """Return persisted scores for map and batch views."""
