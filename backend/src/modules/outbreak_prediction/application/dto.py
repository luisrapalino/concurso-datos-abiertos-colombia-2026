from datetime import datetime

from pydantic import BaseModel, Field

from modules.outbreak_prediction.domain.outbreak_prediction import OutbreakClassification
from shared.territorial import TerritorialCode


class PredictOutbreakQueryDto(BaseModel):
    territorial_code: TerritorialCode
    period: str = Field(
        min_length=7,
        max_length=16,
        pattern=r"^\d{4}-(W\d{2}|01)$",
        description="Epidemiological week (YYYY-Www) or annual period (YYYY-01).",
    )
    event_code: str = Field(default="210", min_length=1, max_length=16)


class FeatureContributionDto(BaseModel):
    feature: str
    contribution: float
    direction: str


class OutbreakPredictionReadDto(BaseModel):
    territorial_code: TerritorialCode
    period: str
    event_code: str
    event_name: str
    outbreak_probability: float
    classification: OutbreakClassification
    model_version: str
    observed_cases: float
    baseline_cases: float
    assumptions: list[str]
    drivers: list[str]
    feature_contributions: list[FeatureContributionDto]
    generated_at: datetime
    persisted: bool = False


class OutbreakMapQueryDto(BaseModel):
    period: str = Field(min_length=7, max_length=16)
    event_code: str = Field(default="210", min_length=1, max_length=16)
    featured_only: bool = Field(
        default=True,
        description="When true, limits the map to curated major municipalities.",
    )
    territorial_codes: str | None = Field(
        default=None,
        description="Optional comma-separated DANE codes (overrides featured_only).",
    )
    limit: int = Field(default=100, ge=1, le=500)


class OutbreakMapPointDto(BaseModel):
    territorial_code: TerritorialCode
    municipality_name: str
    period: str
    event_name: str
    outbreak_probability: float
    classification: OutbreakClassification
    observed_cases: float
    latitude: float
    longitude: float


class OutbreakAlertsQueryDto(BaseModel):
    period: str = Field(min_length=7, max_length=16)
    event_code: str = Field(default="210", min_length=1, max_length=16)
    all_events: bool = Field(
        default=False,
        description="When true, ranks alerts across all transmissible SIVIGILA events.",
    )
    featured_only: bool = Field(default=True)
    territorial_codes: str | None = Field(default=None)
    limit: int = Field(default=10, ge=1, le=50)


class OutbreakAlertDto(BaseModel):
    territorial_code: TerritorialCode
    municipality_name: str
    period: str
    event_code: str
    event_name: str
    outbreak_probability: float
    classification: OutbreakClassification
    observed_cases: float
    baseline_cases: float
    top_driver: str | None = None
