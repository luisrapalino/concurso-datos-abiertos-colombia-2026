from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum


class AnomalySeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


DETECTION_VERSION = "outbreak-cases-median-v1.0.0"
MEDIUM_RATIO_THRESHOLD = 1.5
HIGH_RATIO_THRESHOLD = 2.0


@dataclass(frozen=True, slots=True)
class ObservationWithBaseline:
    territorial_code: str
    period: str
    value: Decimal
    baseline: Decimal
    definition_id: str
    definition_name: str


@dataclass(frozen=True, slots=True)
class AnomalyAlert:
    id: str
    territorial_code: str
    indicator_id: str
    indicator_name: str
    detected_on: date
    severity: AnomalySeverity
    description: str
    baseline_value: float
    observed_value: float


def evaluate_observation(observation: ObservationWithBaseline) -> AnomalyAlert | None:
    if observation.baseline <= 0:
        return None

    ratio = float(observation.value / observation.baseline)
    if ratio < MEDIUM_RATIO_THRESHOLD:
        return None

    severity = (
        AnomalySeverity.HIGH if ratio >= HIGH_RATIO_THRESHOLD else AnomalySeverity.MEDIUM
    )
    year = int(observation.period[:4])
    return AnomalyAlert(
        id=f"anomaly:{observation.definition_id}:{observation.territorial_code}:{observation.period}",
        territorial_code=observation.territorial_code,
        indicator_id=observation.definition_id,
        indicator_name=observation.definition_name,
        detected_on=date(year, 1, 1),
        severity=severity,
        description=(
            "Case count exceeds the national median for the epidemiological period "
            f"(ratio {ratio:.2f}). Requires manual epidemiological review."
        ),
        baseline_value=float(observation.baseline),
        observed_value=float(observation.value),
    )
