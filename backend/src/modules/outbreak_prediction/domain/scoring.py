from datetime import datetime

from modules.outbreak_prediction.domain.outbreak_prediction import (
    DENGUE_EVENT_CODE,
    DENGUE_EVENT_NAME,
    OUTBREAK_RULES_VERSION,
    FeatureContribution,
    OutbreakClassification,
    OutbreakFeatureSnapshot,
    OutbreakPrediction,
)


def classify_outbreak_probability(probability: float) -> OutbreakClassification:
    if probability >= 80:
        return OutbreakClassification.CRITICAL
    if probability >= 60:
        return OutbreakClassification.HIGH
    if probability >= 35:
        return OutbreakClassification.MEDIUM
    return OutbreakClassification.LOW


def compute_outbreak_prediction(
    features: OutbreakFeatureSnapshot,
    *,
    generated_at: datetime,
) -> OutbreakPrediction:
    """Multivariate, explainable outbreak signal from curated public health data."""
    if features.baseline_cases <= 0:
        msg = "Baseline case count must be positive to compute outbreak probability."
        raise ValueError(msg)

    ratio = features.observed_cases / features.baseline_cases
    ratio_component = _clamp((ratio - 1.0) * 35.0 + 25.0)

    growth_component = 15.0
    if features.previous_week_cases is not None and features.previous_week_cases > 0:
        week_over_week = features.observed_cases / features.previous_week_cases
        growth_component = _clamp((week_over_week - 1.0) * 40.0 + 15.0)

    vaccination_gap = _clamp(100.0 - (features.vaccination_coverage_pct or 85.0))
    vaccination_component = _clamp(vaccination_gap * 0.35)

    health_access_gap = _clamp(100.0 - (features.health_access_pct or 90.0))
    health_access_component = _clamp(health_access_gap * 0.25)

    pm25 = features.pm25_ug_m3 or 15.0
    pm25_component = _clamp((pm25 / 25.0) * 25.0)

    probability = _clamp(
        ratio_component * 0.40
        + growth_component * 0.20
        + vaccination_component * 0.15
        + health_access_component * 0.15
        + pm25_component * 0.10,
    )

    contributions = (
        FeatureContribution(
            feature="cases_vs_median",
            contribution=round(ratio_component * 0.40, 2),
            direction="increase" if ratio >= 1.0 else "decrease",
        ),
        FeatureContribution(
            feature="week_over_week_growth",
            contribution=round(growth_component * 0.20, 2),
            direction="increase",
        ),
        FeatureContribution(
            feature="vaccination_gap",
            contribution=round(vaccination_component * 0.15, 2),
            direction="increase" if vaccination_gap > 15 else "decrease",
        ),
        FeatureContribution(
            feature="health_access_gap",
            contribution=round(health_access_component * 0.15, 2),
            direction="increase" if health_access_gap > 10 else "decrease",
        ),
        FeatureContribution(
            feature="pm25_exposure",
            contribution=round(pm25_component * 0.10, 2),
            direction="increase" if pm25 > 15 else "decrease",
        ),
    )

    assumptions = (
        "Outbreak probability combines SIVIGILA case elevation, vaccination coverage, "
        "health access proxy and PM2.5 exposure.",
        "Weekly epidemiological periods use convention YYYY-Www.",
        "Vaccination coverage is expanded from departmental to municipal level.",
        "Not validated for automatic public health activation.",
    )
    drivers = (
        f"Observed {features.event_name} cases: {features.observed_cases:.0f}.",
        f"National median for period: {features.baseline_cases:.1f}.",
        f"Relative ratio vs median: {ratio:.2f}.",
        f"Vaccination coverage: {features.vaccination_coverage_pct or 0:.1f}%.",
        f"Institutional births proxy: {features.health_access_pct or 0:.1f}%.",
        f"PM2.5 annual mean: {pm25:.1f} µg/m³.",
    )

    return OutbreakPrediction(
        territorial_code=features.territorial_code,
        period=features.period,
        event_code=features.event_code or DENGUE_EVENT_CODE,
        event_name=features.event_name or DENGUE_EVENT_NAME,
        outbreak_probability=round(probability, 2),
        classification=classify_outbreak_probability(probability),
        model_version=OUTBREAK_RULES_VERSION,
        observed_cases=features.observed_cases,
        baseline_cases=features.baseline_cases,
        assumptions=assumptions,
        drivers=drivers,
        feature_contributions=contributions,
        generated_at=generated_at,
    )


def _clamp(value: float, *, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return max(minimum, min(maximum, value))
