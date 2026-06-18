from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

from modules.outbreak_prediction.domain.outbreak_prediction import OutbreakPrediction


@dataclass(frozen=True, slots=True)
class OutbreakFeatureBundle:
    territorial_code: str
    period: str
    event_code: str
    event_name: str
    observed_cases: Decimal
    baseline_cases: Decimal
    previous_week_cases: Decimal | None
    vaccination_coverage_pct: Decimal | None
    health_access_pct: Decimal | None
    pm25_ug_m3: Decimal | None


class OutbreakDataPort(Protocol):
    def get_feature_bundle(
        self,
        territorial_code: str,
        period: str,
        *,
        event_code: str,
    ) -> OutbreakFeatureBundle | None:
        """Load multivariate features for outbreak scoring."""


class OutbreakPredictionRepository(Protocol):
    def get(
        self,
        *,
        territorial_code: str,
        period: str,
        event_code: str,
        model_version: str,
    ) -> OutbreakPrediction | None:
        """Return a cached outbreak prediction if available."""

    def save(self, prediction: OutbreakPrediction) -> None:
        """Persist an outbreak prediction."""
