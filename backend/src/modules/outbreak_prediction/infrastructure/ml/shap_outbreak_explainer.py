from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import shap
from sklearn.ensemble import RandomForestClassifier

from modules.outbreak_prediction.domain.outbreak_prediction import FeatureContribution


@dataclass(frozen=True, slots=True)
class OutbreakModelBundle:
    model: RandomForestClassifier
    background: np.ndarray
    feature_names: tuple[str, ...]


def explain_outbreak_prediction(
    bundle: OutbreakModelBundle,
    features: np.ndarray,
) -> tuple[float, tuple[FeatureContribution, ...]]:
    probability = float(bundle.model.predict_proba(features)[0, 1]) * 100.0
    probability = max(0.0, min(100.0, probability))

    explainer = shap.TreeExplainer(bundle.model, data=bundle.background)
    shap_values = explainer.shap_values(features)
    class_values = _positive_class_shap_values(shap_values)

    contributions: list[FeatureContribution] = []
    for index, feature_name in enumerate(bundle.feature_names):
        raw_value = float(class_values[index])
        contributions.append(
            FeatureContribution(
                feature=feature_name,
                contribution=round(abs(raw_value) * 100.0, 2),
                direction="increase" if raw_value >= 0 else "decrease",
            ),
        )

    contributions.sort(key=lambda item: item.contribution, reverse=True)
    return probability, tuple(contributions)


def _positive_class_shap_values(shap_values: object) -> np.ndarray:
    if isinstance(shap_values, list):
        values = np.asarray(shap_values[1 if len(shap_values) > 1 else 0])
    else:
        values = np.asarray(shap_values)
    if values.ndim == 3:
        values = values[0, :, 1] if values.shape[-1] > 1 else values[0, :, 0]
    elif values.ndim == 2:
        values = values[0]
    return values


def build_feature_matrix(snapshot_vector: tuple[float, ...]) -> np.ndarray:
    return np.array([snapshot_vector], dtype=float)
