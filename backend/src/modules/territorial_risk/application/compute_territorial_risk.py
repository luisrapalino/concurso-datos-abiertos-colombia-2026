from datetime import datetime
from decimal import Decimal

from modules.territorial_risk.application.ports.promoted_risk_model_port import (
    PromotedRiskModelPort,
)
from modules.territorial_risk.domain.risk_score import (
    GENERAL_MORTALITY_DEFINITION_ID,
    MortalityObservation,
    RiskScore,
)
from modules.territorial_risk.domain.scoring import classify_score, compute_relative_mortality_score


def compute_territorial_risk_score(
    observation: MortalityObservation,
    *,
    national_median: Decimal,
    generated_at: datetime,
    promoted_model: PromotedRiskModelPort | None = None,
) -> RiskScore:
    """Compute territorial risk using a promoted ML model or rule-based fallback."""
    if promoted_model is not None:
        ml_result = promoted_model.score_with_explanations(
            observed_value=float(observation.value),
            baseline_value=float(national_median),
        )
        if ml_result is not None:
            score, contributions, model_version = ml_result
            ratio = float(observation.value / national_median) if national_median > 0 else 0.0
            classification = classify_score(score)
            assumptions = (
                "Score predicted by the promoted ridge mortality risk model.",
                "Feature contributions computed with SHAP LinearExplainer.",
                "Annual indicators use period convention YYYY-01.",
                "Not validated for operational public health decisions.",
            )
            drivers = (
                f"Observed general mortality rate: {float(observation.value):.4f} per 1000.",
                f"National median for period: {float(national_median):.4f} per 1000.",
                f"Relative ratio vs median: {ratio:.3f}.",
            )
            return RiskScore(
                territorial_code=observation.territorial_code,
                period=observation.period,
                score=round(score, 2),
                classification=classification,
                model_version=model_version,
                observed_value=float(observation.value),
                baseline_value=float(national_median),
                indicator_definition_id=GENERAL_MORTALITY_DEFINITION_ID,
                assumptions=assumptions,
                drivers=drivers,
                feature_contributions=contributions,
                generated_at=generated_at,
            )

    return compute_relative_mortality_score(
        observation,
        national_median=national_median,
        generated_at=generated_at,
    )
