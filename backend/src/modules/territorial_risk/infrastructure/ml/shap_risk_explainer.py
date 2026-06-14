from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import shap
from sklearn.linear_model import Ridge

from modules.territorial_risk.domain.explainability import FeatureContribution

FEATURE_DESCRIPTIONS = {
    "observed_mortality_rate": "Observed territorial general mortality rate per 1000.",
    "national_median": "National median mortality rate for the same period.",
    "mortality_ratio": "Ratio of observed mortality to the national median.",
}


@dataclass(frozen=True, slots=True)
class RiskModelBundle:
    model: Ridge
    background: np.ndarray
    feature_names: tuple[str, ...]


def build_feature_matrix(
    *,
    observed_value: float,
    baseline_value: float,
) -> np.ndarray:
    ratio = observed_value / baseline_value if baseline_value > 0 else 0.0
    return np.array([[observed_value, baseline_value, ratio]], dtype=float)


def explain_ridge_prediction(
    bundle: RiskModelBundle,
    features: np.ndarray,
) -> tuple[float, tuple[FeatureContribution, ...]]:
    raw_score = float(bundle.model.predict(features)[0])
    score = max(0.0, min(100.0, raw_score))
    explainer = shap.LinearExplainer(bundle.model, bundle.background)
    shap_values = explainer.shap_values(features)
    values = shap_values[0] if isinstance(shap_values, list) else shap_values[0]

    contributions: list[FeatureContribution] = []
    for index, feature_name in enumerate(bundle.feature_names):
        feature_value = float(features[0, index])
        contribution = round(float(values[index]), 2)
        contributions.append(
            FeatureContribution(
                feature=feature_name,
                value=feature_value,
                contribution=contribution,
                description=FEATURE_DESCRIPTIONS.get(
                    feature_name,
                    f"SHAP contribution for {feature_name}.",
                ),
            ),
        )
    return score, tuple(contributions)
