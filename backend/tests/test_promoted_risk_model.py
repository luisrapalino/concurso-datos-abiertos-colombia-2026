from decimal import Decimal
from pathlib import Path

import joblib
import numpy as np
import pytest
from sklearn.linear_model import Ridge

from modules.territorial_risk.application.compute_territorial_risk import (
    compute_territorial_risk_score,
)
from modules.territorial_risk.domain.explainability import FeatureContribution
from modules.territorial_risk.domain.risk_score import MortalityObservation
from modules.territorial_risk.infrastructure.ml.model_registry import ModelRegistry


@pytest.fixture
def artifacts_dir(tmp_path: Path) -> Path:
    version = "ridge-mortality-risk-v1.0.0"
    features = np.array(
        [
            [8.0, 4.0, 2.0],
            [4.0, 4.0, 1.0],
            [6.0, 3.0, 2.0],
        ],
        dtype=float,
    )
    targets = np.array([75.0, 50.0, 62.5], dtype=float)
    model = Ridge(alpha=1.0)
    model.fit(features, targets)
    joblib.dump(
        {
            "model": model,
            "background": features,
            "feature_names": [
                "observed_mortality_rate",
                "national_median",
                "mortality_ratio",
            ],
        },
        tmp_path / f"{version}.joblib",
    )
    (tmp_path / f"{version}.json").write_text(
        '{"model_version":"ridge-mortality-risk-v1.0.0"}',
        encoding="utf-8",
    )
    return tmp_path


def test_model_registry_promote_and_rollback(artifacts_dir: Path) -> None:
    registry = ModelRegistry(artifacts_dir)
    assert registry.get_promotion_state().active_version is None

    promoted = registry.promote("ridge-mortality-risk-v1.0.0")
    assert promoted.active_version == "ridge-mortality-risk-v1.0.0"

    rolled_back = registry.rollback()
    assert rolled_back.active_version is None


def test_compute_territorial_risk_score_uses_promoted_model(artifacts_dir: Path) -> None:
    shap = pytest.importorskip("shap")
    del shap

    from modules.territorial_risk.infrastructure.ml.file_promoted_model_adapter import (
        FilePromotedRiskModelAdapter,
    )

    registry = ModelRegistry(artifacts_dir)
    registry.promote("ridge-mortality-risk-v1.0.0")

    class _SettingsStub:
        ml_artifacts_dir = artifacts_dir

    adapter = FilePromotedRiskModelAdapter(_SettingsStub())
    observation = MortalityObservation(
        definition_id="general-mortality-rate",
        territorial_code="05001",
        period="2020-01",
        value=Decimal("8.0"),
    )

    from datetime import UTC, datetime

    risk_score = compute_territorial_risk_score(
        observation,
        national_median=Decimal("4.0"),
        generated_at=datetime.now(tz=UTC),
        promoted_model=adapter,
    )

    assert risk_score.model_version == "ridge-mortality-risk-v1.0.0"
    assert len(risk_score.feature_contributions) == 3
    assert all(
        isinstance(item, FeatureContribution) for item in risk_score.feature_contributions
    )
    assert "SHAP LinearExplainer" in risk_score.assumptions[1]
