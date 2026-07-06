from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

DENGUE_EVENT_CODE = "210"
DENGUE_EVENT_NAME = "DENGUE"
DENGUE_DEFINITION_ID = "dengue-weekly-cases"
VACCINATION_DEFINITION_ID = "dpta-penta-vaccination-coverage"
PM25_DEFINITION_ID = "pm25-annual-mean"
HEALTH_ACCESS_DEFINITION_ID = "institutional-births-coverage"
OUTBREAK_RULES_VERSION = "outbreak-multivariate-v1.0.0"
OUTBREAK_ML_DEFAULT_VERSION = "randomforest-outbreak-v1.0.0"


class OutbreakClassification(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True, slots=True)
class FeatureContribution:
    feature: str
    contribution: float
    direction: str


@dataclass(frozen=True, slots=True)
class OutbreakFeatureSnapshot:
    territorial_code: str
    period: str
    event_code: str
    event_name: str
    observed_cases: float
    baseline_cases: float
    previous_week_cases: float | None
    vaccination_coverage_pct: float | None
    health_access_pct: float | None
    pm25_ug_m3: float | None


@dataclass(frozen=True, slots=True)
class OutbreakPrediction:
    territorial_code: str
    period: str
    event_code: str
    event_name: str
    outbreak_probability: float
    classification: OutbreakClassification
    model_version: str
    observed_cases: float
    baseline_cases: float
    assumptions: tuple[str, ...]
    drivers: tuple[str, ...]
    feature_contributions: tuple[FeatureContribution, ...]
    generated_at: datetime
