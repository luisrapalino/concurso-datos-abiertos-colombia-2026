from modules.outbreak_prediction.application.dto import (
    OutbreakMapPointDto,
    OutbreakMapQueryDto,
    PredictOutbreakQueryDto,
)
from modules.outbreak_prediction.application.predict_outbreak import PredictOutbreakUseCase
from modules.outbreak_prediction.domain.repositories import OutbreakDataPort
from shared.colombia_coordinates import resolve_territorial_coordinates
from shared.divipola_catalog import DivipolaCatalog
from shared.exceptions import EntityNotFoundError
from shared.featured_municipalities import resolve_featured_territorial_codes


class ListOutbreakMapUseCase:
    """Builds a territorial map of outbreak probabilities for a given epidemiological week."""

    def __init__(
        self,
        data_port: OutbreakDataPort,
        predict_outbreak_use_case: PredictOutbreakUseCase,
        *,
        catalog: DivipolaCatalog | None = None,
    ) -> None:
        self._data_port = data_port
        self._predict_outbreak_use_case = predict_outbreak_use_case
        self._catalog = catalog or DivipolaCatalog.from_file()

    def execute(self, query: OutbreakMapQueryDto) -> list[OutbreakMapPointDto]:
        territorial_codes = _resolve_territories(query)
        if not territorial_codes:
            territories = self._data_port.list_territories_with_cases(
                str(query.period),
                event_code=str(query.event_code),
                limit=query.limit,
            )
        else:
            territories = list(territorial_codes[: query.limit])

        points: list[OutbreakMapPointDto] = []
        for territorial_code in territories:
            try:
                prediction = self._predict_outbreak_use_case.execute(
                    PredictOutbreakQueryDto(
                        territorial_code=territorial_code,
                        period=str(query.period),
                        event_code=str(query.event_code),
                    )
                )
            except EntityNotFoundError:
                continue

            latitude, longitude = resolve_territorial_coordinates(territorial_code)
            points.append(
                OutbreakMapPointDto(
                    territorial_code=territorial_code,
                    municipality_name=_municipality_name(self._catalog, territorial_code),
                    period=prediction.period,
                    event_name=prediction.event_name,
                    outbreak_probability=prediction.outbreak_probability,
                    classification=prediction.classification,
                    observed_cases=prediction.observed_cases,
                    latitude=latitude,
                    longitude=longitude,
                )
            )
        return points


def _resolve_territories(query: OutbreakMapQueryDto) -> tuple[str, ...]:
    if query.territorial_codes:
        codes = [code.strip() for code in query.territorial_codes.split(",") if code.strip()]
        return resolve_featured_territorial_codes(territorial_codes=codes, featured_only=False)
    if query.featured_only:
        return resolve_featured_territorial_codes(featured_only=True)
    return ()


def _municipality_name(catalog: DivipolaCatalog, territorial_code: str) -> str:
    name = catalog.municipality_name(territorial_code)
    return name.title() if name else territorial_code
