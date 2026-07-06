from pathlib import Path

import joblib
import numpy as np
import pytest
from sklearn.ensemble import RandomForestClassifier

from modules.outbreak_prediction.domain.feature_engineering import OUTBREAK_ML_FEATURE_NAMES
from modules.outbreak_prediction.domain.outbreak_prediction import OutbreakFeatureSnapshot
from modules.outbreak_prediction.domain.scoring import compute_outbreak_prediction
from modules.outbreak_prediction.infrastructure.ml.outbreak_model_registry import (
    OutbreakModelRegistry,
)


@pytest.fixture
def artifacts_dir(tmp_path: Path) -> Path:
    version = "randomforest-outbreak-v1.0.0"
    features = np.array(
        [
            [2.0, 1.0, 3.0, 1.5, 2.0, 70.0, 30.0, 85.0, 15.0, 20.0, 0.0, 1.0, 1.0, 1.0, 0.5],
            [0.5, 1.2, 0.4, 0.4, 0.9, 95.0, 5.0, 98.0, 2.0, 10.0, 0.0, 1.0, 0.0, 0.0, 0.1],
            [1.8, 1.1, 2.5, 1.2, 1.8, 75.0, 25.0, 88.0, 12.0, 18.0, 0.5, 0.8, 1.0, 1.0, 0.4],
        ],
        dtype=float,
    )
    labels = np.array([1, 0, 1], dtype=int)
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(features, labels)
    joblib.dump(
        {
            "model": model,
            "background": features,
            "feature_names": list(OUTBREAK_ML_FEATURE_NAMES),
        },
        tmp_path / f"{version}.joblib",
    )
    (tmp_path / f"{version}.json").write_text(
        '{"model_version":"randomforest-outbreak-v1.0.0"}',
        encoding="utf-8",
    )
    return tmp_path


def test_outbreak_model_registry_promote_and_rollback(artifacts_dir: Path) -> None:
    registry = OutbreakModelRegistry(artifacts_dir)
    assert registry.get_promotion_state().active_version is None

    promoted = registry.promote("randomforest-outbreak-v1.0.0")
    assert promoted.active_version == "randomforest-outbreak-v1.0.0"

    rolled_back = registry.rollback()
    assert rolled_back.active_version is None


def test_compute_outbreak_prediction_uses_promoted_random_forest(artifacts_dir: Path) -> None:
    pytest.importorskip("shap")

    from datetime import UTC, datetime

    from modules.outbreak_prediction.infrastructure.ml.file_promoted_outbreak_model_adapter import (
        FilePromotedOutbreakModelAdapter,
    )

    registry = OutbreakModelRegistry(artifacts_dir)
    registry.promote("randomforest-outbreak-v1.0.0")

    class _SettingsStub:
        ml_artifacts_dir = artifacts_dir

    adapter = FilePromotedOutbreakModelAdapter(_SettingsStub())
    snapshot = OutbreakFeatureSnapshot(
        territorial_code="05001",
        period="2020-W33",
        event_code="210",
        event_name="DENGUE",
        observed_cases=120.0,
        baseline_cases=30.0,
        previous_week_cases=60.0,
        vaccination_coverage_pct=70.0,
        health_access_pct=85.0,
        pm25_ug_m3=20.0,
    )

    prediction = compute_outbreak_prediction(
        snapshot,
        generated_at=datetime.now(tz=UTC),
        promoted_model=adapter,
    )

    assert prediction.model_version == "randomforest-outbreak-v1.0.0"
    assert len(prediction.feature_contributions) == len(OUTBREAK_ML_FEATURE_NAMES)
    assert "SHAP TreeExplainer" in prediction.assumptions[1]
