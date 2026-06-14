from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from modules.territorial_risk.domain.explainability import FeatureContribution


class RiskClassification(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


GENERAL_MORTALITY_DEFINITION_ID = "general-mortality-rate"
RULES_VERSION = "mortality-relative-v1.0.0"


@dataclass(frozen=True, slots=True)
class MortalityObservation:
    definition_id: str
    territorial_code: str
    period: str
    value: Decimal


@dataclass(frozen=True, slots=True)
class RiskScore:
    territorial_code: str
    period: str
    score: float
    classification: RiskClassification
    model_version: str
    observed_value: float
    baseline_value: float
    indicator_definition_id: str
    assumptions: tuple[str, ...]
    drivers: tuple[str, ...]
    feature_contributions: tuple[FeatureContribution, ...]
    generated_at: datetime
