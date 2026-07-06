from datetime import UTC, datetime

import pytest

from modules.outbreak_prediction.domain.feature_engineering import (
    OUTBREAK_ML_FEATURE_NAMES,
    build_outbreak_feature_vector,
    outbreak_alert_label,
)
from modules.outbreak_prediction.domain.outbreak_prediction import OutbreakFeatureSnapshot
from modules.outbreak_prediction.domain.scoring import (
    compute_outbreak_prediction,
    compute_rule_based_outbreak_prediction,
)


def _snapshot(**overrides: object) -> OutbreakFeatureSnapshot:
    base = {
        "territorial_code": "05001",
        "period": "2020-W33",
        "event_code": "210",
        "event_name": "DENGUE",
        "observed_cases": 120.0,
        "baseline_cases": 30.0,
        "previous_week_cases": 60.0,
        "vaccination_coverage_pct": 70.0,
        "health_access_pct": 85.0,
        "pm25_ug_m3": 20.0,
    }
    base.update(overrides)
    return OutbreakFeatureSnapshot(**base)


def test_feature_vector_has_fifteen_intermediate_features() -> None:
    vector = build_outbreak_feature_vector(_snapshot())
    assert len(vector) == 15
    assert len(OUTBREAK_ML_FEATURE_NAMES) == 15


def test_outbreak_alert_label_detects_elevated_signal() -> None:
    assert outbreak_alert_label(_snapshot()) == 1
    assert outbreak_alert_label(_snapshot(observed_cases=5.0, baseline_cases=20.0, previous_week_cases=6.0)) == 0


def test_compute_rule_based_outbreak_prediction_high_signal() -> None:
    prediction = compute_rule_based_outbreak_prediction(
        _snapshot(),
        generated_at=datetime.now(tz=UTC),
    )

    assert prediction.outbreak_probability >= 50
    assert prediction.classification.value in {"high", "critical", "medium"}
    assert len(prediction.feature_contributions) == 5
    assert prediction.model_version == "outbreak-multivariate-v1.0.0"


def test_compute_rule_based_outbreak_prediction_low_signal() -> None:
    prediction = compute_rule_based_outbreak_prediction(
        _snapshot(
            observed_cases=5.0,
            baseline_cases=20.0,
            previous_week_cases=6.0,
            vaccination_coverage_pct=95.0,
            health_access_pct=98.0,
            pm25_ug_m3=10.0,
        ),
        generated_at=datetime.now(tz=UTC),
    )

    assert prediction.outbreak_probability < 50
    assert prediction.classification.value == "low"


class _FakePromotedModel:
    def active_model_version(self) -> str:
        return "randomforest-outbreak-v1.0.0"

    def score_with_explanations(self, *, features: OutbreakFeatureSnapshot):
        del features
        from modules.outbreak_prediction.domain.outbreak_prediction import FeatureContribution

        return (
            72.5,
            (
                FeatureContribution(
                    feature="cases_vs_median",
                    contribution=18.0,
                    direction="increase",
                ),
            ),
            "randomforest-outbreak-v1.0.0",
        )


def test_compute_outbreak_prediction_uses_promoted_model_when_available() -> None:
    prediction = compute_outbreak_prediction(
        _snapshot(),
        generated_at=datetime.now(tz=UTC),
        promoted_model=_FakePromotedModel(),
    )

    assert prediction.model_version == "randomforest-outbreak-v1.0.0"
    assert prediction.outbreak_probability == pytest.approx(72.5)
    assert "SHAP TreeExplainer" in prediction.assumptions[1]
