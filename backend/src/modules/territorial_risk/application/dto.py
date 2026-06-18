from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from shared.period import Period
from shared.territorial import TerritorialCode


class RiskClassification(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PredictRiskQueryDto(BaseModel):
    territorial_code: TerritorialCode
    period: Period


class FeatureContributionReadDto(BaseModel):
    feature: str
    value: float
    contribution: float
    description: str


class RiskScoreReadDto(BaseModel):
    territorial_code: TerritorialCode
    period: Period
    score: float = Field(ge=0, le=100, description="Normalized territorial risk score.")
    classification: RiskClassification
    model_version: str
    indicator_definition_id: str
    observed_value: float
    baseline_value: float
    assumptions: list[str]
    drivers: list[str]
    feature_contributions: list[FeatureContributionReadDto]
    generated_at: datetime
    persisted: bool = Field(
        default=False,
        description="Whether the score is stored for audit and map views.",
    )


class TerritorialRiskMapQueryDto(BaseModel):
    period: Period
    definition_id: str = Field(default="general-mortality-rate", min_length=1)
    featured_only: bool = Field(
        default=True,
        description="When true, limits the map to curated major municipalities.",
    )
    territorial_codes: str | None = Field(
        default=None,
        description="Optional comma-separated DANE codes (overrides featured_only).",
    )
    limit: int = Field(default=200, ge=1, le=500)


class TerritorialRiskMapPointDto(BaseModel):
    territorial_code: TerritorialCode
    municipality_name: str
    period: Period
    score: float = Field(ge=0, le=100)
    classification: RiskClassification
    latitude: float
    longitude: float
