from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FeatureContribution:
    feature: str
    value: float
    contribution: float
    description: str


def decompose_relative_mortality_score(
    *,
    observed_value: float,
    baseline_value: float,
    ratio: float,
) -> tuple[FeatureContribution, ...]:
    """Rule-based score decomposition for auditable explainability."""
    relative_delta = (ratio - 1.0) * 50.0
    return (
        FeatureContribution(
            feature="neutral_baseline",
            value=baseline_value,
            contribution=50.0,
            description="Neutral score anchor before territorial deviation.",
        ),
        FeatureContribution(
            feature="mortality_ratio_delta",
            value=round(ratio, 4),
            contribution=round(relative_delta, 2),
            description="Adjustment from territorial mortality relative to national median.",
        ),
        FeatureContribution(
            feature="observed_mortality_rate",
            value=observed_value,
            contribution=round(50.0 + relative_delta, 2),
            description="Final bounded score derived from observed mortality.",
        ),
    )
