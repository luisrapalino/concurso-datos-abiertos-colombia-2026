from typing import Protocol

from modules.outbreak_prediction.domain.outbreak_prediction import (
    FeatureContribution,
    OutbreakFeatureSnapshot,
)


class PromotedOutbreakModelPort(Protocol):
    def active_model_version(self) -> str | None:
        """Return the promoted outbreak model version, if any."""

    def score_with_explanations(
        self,
        *,
        features: OutbreakFeatureSnapshot,
    ) -> tuple[float, tuple[FeatureContribution, ...], str] | None:
        """Return probability (0-100), SHAP contributions, and model version."""
