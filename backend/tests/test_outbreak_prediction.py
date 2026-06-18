from datetime import UTC, datetime

import pytest

from modules.outbreak_prediction.domain.outbreak_prediction import OutbreakFeatureSnapshot
from modules.outbreak_prediction.domain.scoring import compute_outbreak_prediction


def test_compute_outbreak_prediction_high_signal() -> None:
    prediction = compute_outbreak_prediction(
        OutbreakFeatureSnapshot(
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
        ),
        generated_at=datetime.now(tz=UTC),
    )

    assert prediction.outbreak_probability >= 50
    assert prediction.classification.value in {"high", "critical", "medium"}
    assert len(prediction.feature_contributions) == 5
    assert prediction.model_version == "outbreak-multivariate-v1.0.0"


def test_compute_outbreak_prediction_low_signal() -> None:
    prediction = compute_outbreak_prediction(
        OutbreakFeatureSnapshot(
            territorial_code="05001",
            period="2020-W10",
            event_code="210",
            event_name="DENGUE",
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
