from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import joblib

from config.settings import Settings, get_settings
from modules.outbreak_prediction.application.ports.promoted_outbreak_model_port import (
    PromotedOutbreakModelPort,
)
from modules.outbreak_prediction.domain.feature_engineering import build_outbreak_feature_vector
from modules.outbreak_prediction.domain.outbreak_prediction import (
    FeatureContribution,
    OutbreakFeatureSnapshot,
)
from modules.outbreak_prediction.infrastructure.ml.outbreak_model_registry import (
    OutbreakModelRegistry,
)
from modules.outbreak_prediction.infrastructure.ml.shap_outbreak_explainer import (
    OutbreakModelBundle,
    build_feature_matrix,
    explain_outbreak_prediction,
)


class NullPromotedOutbreakModelAdapter:
    """Fallback adapter when outbreak ML serving is disabled."""

    def active_model_version(self) -> str | None:
        return None

    def score_with_explanations(
        self,
        *,
        features: OutbreakFeatureSnapshot,
    ) -> tuple[float, tuple[FeatureContribution, ...], str] | None:
        del features
        return None


class FilePromotedOutbreakModelAdapter(PromotedOutbreakModelPort):
    """Loads promoted Random Forest outbreak models from the artifact registry."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._registry = OutbreakModelRegistry(resolve_outbreak_artifacts_dir(self._settings))

    def active_model_version(self) -> str | None:
        return self._registry.get_promotion_state().active_version

    def score_with_explanations(
        self,
        *,
        features: OutbreakFeatureSnapshot,
    ) -> tuple[float, tuple[FeatureContribution, ...], str] | None:
        version = self.active_model_version()
        if version is None:
            return None

        bundle = _load_outbreak_model_bundle(version, str(self._registry.artifacts_dir))
        matrix = build_feature_matrix(build_outbreak_feature_vector(features))
        probability, contributions = explain_outbreak_prediction(bundle, matrix)
        return probability, contributions, version


def resolve_outbreak_artifacts_dir(settings: Settings) -> Path:
    if settings.ml_artifacts_dir is not None:
        return settings.ml_artifacts_dir
    backend_root = Path(__file__).resolve().parents[5]
    return backend_root / "ml" / "artifacts"


@lru_cache(maxsize=4)
def _load_outbreak_model_bundle(version: str, artifacts_dir: str) -> OutbreakModelBundle:
    artifact_path = Path(artifacts_dir) / f"{version}.joblib"
    payload = joblib.load(artifact_path)
    return OutbreakModelBundle(
        model=payload["model"],
        background=payload["background"],
        feature_names=tuple(payload["feature_names"]),
    )


def load_outbreak_model_metadata(version: str, artifacts_dir: Path) -> dict[str, object]:
    metadata_path = artifacts_dir / f"{version}.json"
    return json.loads(metadata_path.read_text(encoding="utf-8"))
