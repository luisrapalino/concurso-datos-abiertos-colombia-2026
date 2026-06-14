from pydantic import BaseModel, Field


class ApiErrorDetail(BaseModel):
    """Single validation or domain error detail."""

    field: str | None = None
    message: str


class ApiErrorResponse(BaseModel):
    """Consistent HTTP error payload."""

    code: str = Field(description="Machine-readable error code.")
    message: str = Field(description="Human-readable summary.")
    details: list[ApiErrorDetail] = Field(default_factory=list)
