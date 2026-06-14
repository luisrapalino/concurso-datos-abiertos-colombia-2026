from modules.health_indicators.application.dto import (
    HealthIndicatorReadDto,
    ListHealthIndicatorsQueryDto,
)
from modules.health_indicators.domain.health_indicator import HealthIndicator
from modules.health_indicators.domain.repositories import (
    HealthIndicatorRepository,
    ListHealthIndicatorsQuery,
)


def _to_dto(entity: HealthIndicator) -> HealthIndicatorReadDto:
    return HealthIndicatorReadDto(
        id=entity.id,
        definition_id=entity.definition_id,
        name=entity.name,
        territorial_code=entity.territorial_code,
        period=entity.period,
        value=float(entity.value),
        measurement_unit=entity.measurement_unit,
        source_id=entity.source_id,
        ingested_at=entity.ingested_at,
    )


class ListHealthIndicatorsUseCase:
    """Lists curated territorial health indicator observations."""

    def __init__(self, repository: HealthIndicatorRepository) -> None:
        self._repository = repository

    def execute(self, query: ListHealthIndicatorsQueryDto) -> list[HealthIndicatorReadDto]:
        domain_query = ListHealthIndicatorsQuery(
            territorial_code=str(query.territorial_code) if query.territorial_code else None,
            period=str(query.period) if query.period else None,
            definition_id=query.definition_id,
            limit=query.limit,
        )
        return [_to_dto(item) for item in self._repository.list_observations(domain_query)]
