from pydantic import BaseModel, Field


class MunicipalityReadDto(BaseModel):
    territorial_code: str
    name: str
    department_code: str
    display_name: str


class SearchMunicipalitiesQueryDto(BaseModel):
    search: str = Field(min_length=1, max_length=80)
    limit: int = Field(default=8, ge=1, le=25)
