from enum import StrEnum

from pydantic import BaseModel, Field

from shared.period import Period
from shared.territorial import TerritorialCode


class TrendPointKind(StrEnum):
    HISTORICAL = "historical"
    FORECAST = "forecast"


class TerritorialTrendsQueryDto(BaseModel):
    territorial_code: TerritorialCode
    indicator_id: str = Field(default="stub-mortality-rate", min_length=1)
    horizon_weeks: int = Field(default=4, ge=1, le=12)


class TrendPointDto(BaseModel):
    period: Period
    value: float
    kind: TrendPointKind


class TerritorialTrendReadDto(BaseModel):
    territorial_code: TerritorialCode
    indicator_id: str
    indicator_name: str
    points: list[TrendPointDto]
    forecast_horizon_weeks: int
    model_version: str
