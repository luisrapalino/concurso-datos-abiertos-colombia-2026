from pydantic import BaseModel, Field


class MunicipalVariableDatasetDto(BaseModel):
    territorial_code: str
    municipality_name: str
    definition_id: str
    variable_name: str
    active_binding_id: str
    source_id: str
    api_url: str
    portal_url: str
    provider: str
    granularity: str
    selection_note: str
    fallback_binding_ids: list[str] = Field(default_factory=list)
    records_ingested: int = 0
    latest_period: str | None = None
    resolution_note: str = Field(
        default="Dataset seleccionado por prioridad y disponibilidad municipal.",
    )
