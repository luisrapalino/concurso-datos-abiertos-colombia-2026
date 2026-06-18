from modules.outbreak_prediction.application.dto import (
    OutbreakAlertDto,
    OutbreakAlertsQueryDto,
    PredictOutbreakQueryDto,
)
from modules.outbreak_prediction.application.predict_outbreak import PredictOutbreakUseCase
from modules.outbreak_prediction.domain.repositories import OutbreakDataPort
from shared.divipola_catalog import DivipolaCatalog
from shared.exceptions import EntityNotFoundError
from shared.featured_municipalities import resolve_featured_territorial_codes
from shared.sivigila_events import TRANSMISSIBLE_SIVIGILA_EVENTS


class ListOutbreakAlertsUseCase:
    """Ranks municipalities by outbreak signal for territorial prioritization."""

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

    def execute(self, query: OutbreakAlertsQueryDto) -> list[OutbreakAlertDto]:
        event_codes = (
            tuple(event.code for event in TRANSMISSIBLE_SIVIGILA_EVENTS)
            if query.all_events
            else (str(query.event_code),)
        )

        alerts: list[OutbreakAlertDto] = []
        for event_code in event_codes:
            territorial_codes = _resolve_territories(query, self._data_port, event_code=event_code)
            for territorial_code in territorial_codes:
                try:
                    prediction = self._predict_outbreak_use_case.execute(
                        PredictOutbreakQueryDto(
                            territorial_code=territorial_code,
                            period=str(query.period),
                            event_code=event_code,
                        )
                    )
                except EntityNotFoundError:
                    continue

                top_driver = prediction.drivers[0] if prediction.drivers else None
                alerts.append(
                    OutbreakAlertDto(
                        territorial_code=territorial_code,
                        municipality_name=_municipality_name(self._catalog, territorial_code),
                        period=prediction.period,
                        event_code=prediction.event_code,
                        event_name=prediction.event_name,
                        outbreak_probability=prediction.outbreak_probability,
                        classification=prediction.classification,
                        observed_cases=prediction.observed_cases,
                        baseline_cases=prediction.baseline_cases,
                        top_driver=top_driver,
                    )
                )

        alerts.sort(
            key=lambda alert: (alert.outbreak_probability, alert.observed_cases),
            reverse=True,
        )
        return alerts[: query.limit]


def _resolve_territories(
    query: OutbreakAlertsQueryDto,
    data_port: OutbreakDataPort,
    *,
    event_code: str,
) -> tuple[str, ...]:
    if query.territorial_codes:
        codes = [code.strip() for code in query.territorial_codes.split(",") if code.strip()]
        return resolve_featured_territorial_codes(territorial_codes=codes, featured_only=False)
    if query.featured_only:
        return resolve_featured_territorial_codes(featured_only=True)
    return tuple(
        data_port.list_territories_with_cases(
            str(query.period),
            event_code=event_code,
            limit=query.limit * 3,
        )
    )


def _municipality_name(catalog: DivipolaCatalog, territorial_code: str) -> str:
    name = catalog.municipality_name(territorial_code)
    return name.title() if name else territorial_code
