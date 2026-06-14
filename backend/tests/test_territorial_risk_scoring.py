from datetime import UTC, datetime
from decimal import Decimal

import pytest

from modules.territorial_risk.domain.risk_score import MortalityObservation, RiskClassification
from modules.territorial_risk.domain.scoring import classify_score, compute_relative_mortality_score


def test_classify_score_thresholds() -> None:
    assert classify_score(20) == RiskClassification.LOW
    assert classify_score(50) == RiskClassification.MEDIUM
    assert classify_score(70) == RiskClassification.HIGH
    assert classify_score(90) == RiskClassification.CRITICAL


def test_compute_relative_mortality_score_at_median_is_neutral() -> None:
    observation = MortalityObservation(
        definition_id="general-mortality-rate",
        territorial_code="05001",
        period="2020-01",
        value=Decimal("8.0"),
    )
    result = compute_relative_mortality_score(
        observation,
        national_median=Decimal("8.0"),
        generated_at=datetime.now(tz=UTC),
    )
    assert result.score == 50.0
    assert result.classification == RiskClassification.MEDIUM
    assert result.observed_value == 8.0
    assert result.baseline_value == 8.0


def test_compute_relative_mortality_score_above_median_increases_risk() -> None:
    observation = MortalityObservation(
        definition_id="general-mortality-rate",
        territorial_code="05001",
        period="2020-01",
        value=Decimal("12.0"),
    )
    result = compute_relative_mortality_score(
        observation,
        national_median=Decimal("8.0"),
        generated_at=datetime.now(tz=UTC),
    )
    assert result.score == pytest.approx(75.0)
    assert result.classification == RiskClassification.HIGH
