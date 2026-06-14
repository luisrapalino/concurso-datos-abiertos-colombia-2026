from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import joblib

from config.settings import Settings, get_settings
from modules.territorial_risk.application.ports.promoted_risk_model_port import (
    PromotedRiskModelPort,
)
from modules.territorial_risk.domain.explainability import FeatureContribution
from modules.territorial_risk.infrastructure.ml.model_registry import ModelRegistry
from modules.territorial_risk.infrastructure.ml.shap_risk_explainer import (
    RiskModelBundle,
    build_feature_matrix,
    explain_ridge_prediction,
)


class NullPromotedRiskModelAdapter:
    """Fallback adapter when ML serving is disabled."""

    def active_model_version(self) -> str | None:
        return None

    def score_with_explanations(
        self,
        *,
        observed_value: float,
        baseline_value: float,
    ) -> tuple[float, tuple[FeatureContribution, ...], str] | None:
        del observed_value, baseline_value
        return None


class FilePromotedRiskModelAdapter(PromotedRiskModelPort):
    """Loads promoted ridge models from the local artifact registry."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._registry = ModelRegistry(resolve_artifacts_dir(self._settings))

    def active_model_version(self) -> str | None:
        return self._registry.get_promotion_state().active_version

    def score_with_explanations(
        self,
        *,
        observed_value: float,
        baseline_value: float,
    ) -> tuple[float, tuple[FeatureContribution, ...], str] | None:
        version = self.active_model_version()
        if version is None:
            return None

        bundle = _load_model_bundle(version, str(self._registry.artifacts_dir))
        features = build_feature_matrix(
            observed_value=observed_value,
            baseline_value=baseline_value,
        )
        score, contributions = explain_ridge_prediction(bundle, features)
        return score, contributions, version


def resolve_artifacts_dir(settings: Settings) -> Path:
    if settings.ml_artifacts_dir is not None:
        return settings.ml_artifacts_dir
    backend_root = Path(__file__).resolve().parents[5]
    return backend_root / "ml" / "artifacts"


@lru_cache(maxsize=4)
def _load_model_bundle(version: str, artifacts_dir: str) -> RiskModelBundle:
    artifact_path = Path(artifacts_dir) / f"{version}.joblib"
    payload = joblib.load(artifact_path)
    return RiskModelBundle(
        model=payload["model"],
        background=payload["background"],
        feature_names=tuple(payload["feature_names"]),
    )


def load_model_metadata(version: str, artifacts_dir: Path) -> dict[str, object]:
    metadata_path = artifacts_dir / f"{version}.json"
    return json.loads(metadata_path.read_text(encoding="utf-8"))
