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


class RiskScoreReadDto(BaseModel):
    territorial_code: TerritorialCode
    period: Period
    score: float = Field(ge=0, le=100, description="Normalized territorial risk score.")
    classification: RiskClassification
    model_version: str
    assumptions: list[str]
    generated_at: datetime
