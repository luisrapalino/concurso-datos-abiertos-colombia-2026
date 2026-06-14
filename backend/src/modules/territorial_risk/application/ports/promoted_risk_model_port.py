from typing import Protocol

from modules.territorial_risk.domain.explainability import FeatureContribution


class PromotedRiskModelPort(Protocol):
    """Serving port for promoted ML risk models with SHAP explanations."""

    def active_model_version(self) -> str | None:
        """Return the promoted model version, if any."""

    def score_with_explanations(
        self,
        *,
        observed_value: float,
        baseline_value: float,
    ) -> tuple[float, tuple[FeatureContribution, ...], str] | None:
        """Return bounded score, SHAP contributions, and model version."""
