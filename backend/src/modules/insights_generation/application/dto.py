from enum import StrEnum

from pydantic import BaseModel, Field

from shared.territorial import TerritorialCode


class InsightConfidence(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ListInsightsQueryDto(BaseModel):
    territorial_code: TerritorialCode
    limit: int = Field(default=5, ge=1, le=20)


class InsightReadDto(BaseModel):
    id: str
    territorial_code: TerritorialCode
    title: str
    narrative: str
    confidence: InsightConfidence
    data_version: str
    sources: list[str]
    analysis_period: str | None = None
    system_context: str | None = Field(
        default=None,
        description="Explains data window, models and limits of the narrative.",
    )
