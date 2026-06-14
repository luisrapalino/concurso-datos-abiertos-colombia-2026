from datetime import datetime
from decimal import Decimal

from modules.territorial_risk.domain.risk_score import (
    GENERAL_MORTALITY_DEFINITION_ID,
    RULES_VERSION,
    MortalityObservation,
    RiskClassification,
    RiskScore,
)


def classify_score(score: float) -> RiskClassification:
    if score >= 80:
        return RiskClassification.CRITICAL
    if score >= 60:
        return RiskClassification.HIGH
    if score >= 35:
        return RiskClassification.MEDIUM
    return RiskClassification.LOW


def compute_relative_mortality_score(
    observation: MortalityObservation,
    *,
    national_median: Decimal,
    generated_at: datetime,
) -> RiskScore:
    """Score territory by comparing mortality to the national median for the period."""
    if national_median <= 0:
        msg = "National median must be positive to compute relative risk."
        raise ValueError(msg)

    territorial_value = observation.value
    ratio = float(territorial_value / national_median)
    score = max(0.0, min(100.0, 50.0 + (ratio - 1.0) * 50.0))
    classification = classify_score(score)

    assumptions = (
        "Score compares territorial general mortality to the national median for the same period.",
        "Annual indicators use period convention YYYY-01.",
        "Not validated for operational public health decisions.",
    )
    drivers = (
        f"Observed general mortality rate: {float(territorial_value):.4f} per 1000.",
        f"National median for period: {float(national_median):.4f} per 1000.",
        f"Relative ratio vs median: {ratio:.3f}.",
    )

    return RiskScore(
        territorial_code=observation.territorial_code,
        period=observation.period,
        score=round(score, 2),
        classification=classification,
        model_version=RULES_VERSION,
        observed_value=float(territorial_value),
        baseline_value=float(national_median),
        indicator_definition_id=GENERAL_MORTALITY_DEFINITION_ID,
        assumptions=assumptions,
        drivers=drivers,
        generated_at=generated_at,
    )
