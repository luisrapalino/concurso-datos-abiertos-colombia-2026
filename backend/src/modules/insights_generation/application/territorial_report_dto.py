from datetime import datetime

from pydantic import BaseModel, Field

from modules.insights_generation.application.dto import InsightReadDto
from modules.territorial_risk.application.dto import RiskScoreReadDto
from shared.period import Period
from shared.territorial import TerritorialCode


class TerritorialReportQueryDto(BaseModel):
    territorial_code: TerritorialCode
    period: Period
    insight_limit: int = Field(default=3, ge=1, le=10)


class TerritorialReportReadDto(BaseModel):
    territorial_code: TerritorialCode
    period: Period
    generated_at: datetime
    risk: RiskScoreReadDto
    insights: list[InsightReadDto]
    drift_status: str
    drift_note: str
    disclaimer: str = Field(
        default=(
            "Informe exploratorio basado en datos abiertos; no sustituye validación "
            "epidemiológica ni decisiones institucionales."
        ),
    )
