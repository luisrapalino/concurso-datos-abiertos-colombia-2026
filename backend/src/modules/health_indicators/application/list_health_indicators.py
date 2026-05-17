from modules.health_indicators.application.dto import HealthIndicatorReadDto
from modules.health_indicators.domain.health_indicator import HealthIndicator
from modules.health_indicators.domain.repositories import HealthIndicatorRepository


def _to_dto(entity: HealthIndicator) -> HealthIndicatorReadDto:
    return HealthIndicatorReadDto(
        id=entity.id,
        name=entity.name,
        territorial_code=entity.territorial_code,
        measurement_unit=entity.measurement_unit,
    )


class ListHealthIndicatorsUseCase:
    """Lists health indicator definitions sourced from persistence."""

    def __init__(self, repository: HealthIndicatorRepository) -> None:
        self._repository = repository

    def execute(self) -> list[HealthIndicatorReadDto]:
        return [_to_dto(item) for item in self._repository.list_all()]
