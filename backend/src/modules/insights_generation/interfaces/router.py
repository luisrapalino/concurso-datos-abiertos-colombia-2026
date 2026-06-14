from typing import Annotated

from fastapi import APIRouter, Depends, Query

from modules.insights_generation.application.dto import InsightReadDto, ListInsightsQueryDto
from modules.insights_generation.application.generate_insights import GenerateInsightsUseCase

router = APIRouter(tags=["insights"])


def get_generate_insights_use_case() -> GenerateInsightsUseCase:
    return GenerateInsightsUseCase()


@router.get("/insights", response_model=list[InsightReadDto])
def list_insights(
    query: Annotated[ListInsightsQueryDto, Query()],
    use_case: Annotated[GenerateInsightsUseCase, Depends(get_generate_insights_use_case)],
) -> list[InsightReadDto]:
    return use_case.execute(query)
