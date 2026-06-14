from datetime import datetime

from pydantic import BaseModel, Field

from shared.period import Period
from shared.territorial import TerritorialCode


class ListHealthIndicatorsQueryDto(BaseModel):
    territorial_code: TerritorialCode | None = None
    period: Period | None = None
    definition_id: str | None = Field(default=None, min_length=1)
    limit: int = Field(default=100, ge=1, le=500)


class HealthIndicatorReadDto(BaseModel):
    id: str = Field(description="Stable identifier for the territorial observation.")
    definition_id: str
    name: str
    territorial_code: TerritorialCode
    period: Period
    value: float
    measurement_unit: str
    source_id: str
    ingested_at: datetime | None = None
