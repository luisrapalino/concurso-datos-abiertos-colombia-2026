from pydantic import BaseModel, Field

from shared.period import Period


class DepartmentMortalitySummaryDto(BaseModel):
    department_code: str
    department_name: str
    observation_count: int
    mean_mortality: float


class BiasAnalysisReadDto(BaseModel):
    definition_id: str
    period: Period
    national_mean: float
    departments: list[DepartmentMortalitySummaryDto]
    analysis_note: str = Field(
        default=(
            "Comparación descriptiva por departamento; no implica causalidad ni "
            "control por confusores socio-demográficos."
        ),
    )
