from datetime import date
from enum import StrEnum

from pydantic import BaseModel, Field

from shared.territorial import TerritorialCode


class AnomalySeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ListAnomaliesQueryDto(BaseModel):
    territorial_code: TerritorialCode | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class AnomalyAlertReadDto(BaseModel):
    id: str
    territorial_code: TerritorialCode
    indicator_id: str
    indicator_name: str
    detected_on: date
    severity: AnomalySeverity
    description: str
    baseline_value: float
    observed_value: float


class AnomalyAlertPageDto(BaseModel):
    items: list[AnomalyAlertReadDto]
    page: int
    page_size: int
    total_items: int
    total_pages: int
