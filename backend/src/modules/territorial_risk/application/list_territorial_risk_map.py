from modules.territorial_risk.application.dto import (
    PredictRiskQueryDto,
    TerritorialRiskMapPointDto,
    TerritorialRiskMapQueryDto,
)
from modules.territorial_risk.application.predict_risk import PredictRiskUseCase
from modules.territorial_risk.domain.repositories import TerritorialRiskDataPort
from shared.colombia_coordinates import resolve_territorial_coordinates
from shared.divipola_catalog import DivipolaCatalog
from shared.exceptions import EntityNotFoundError
from shared.featured_municipalities import resolve_featured_territorial_codes


class ListTerritorialRiskMapUseCase:
    """Builds map-ready risk points for a period, computing missing scores on demand."""

    def __init__(
        self,
        data_port: TerritorialRiskDataPort,
        predict_risk_use_case: PredictRiskUseCase,
        *,
        catalog: DivipolaCatalog | None = None,
    ) -> None:
        self._data_port = data_port
        self._predict_risk_use_case = predict_risk_use_case
        self._catalog = catalog or DivipolaCatalog.from_file()

    def execute(self, query: TerritorialRiskMapQueryDto) -> list[TerritorialRiskMapPointDto]:
        period = str(query.period)
        national_median = self._data_port.get_national_median_mortality(period)
        if national_median is None:
            raise EntityNotFoundError("national_mortality_baseline", period)

        territorial_codes = _resolve_territories(query)
        if not territorial_codes:
            territorial_codes = tuple(
                self._data_port.list_territorial_codes_for_period(
                    period,
                    definition_id=query.definition_id,
                    limit=query.limit,
                )
            )
        if not territorial_codes:
            raise EntityNotFoundError("territorial_risk_map", period)

        points: list[TerritorialRiskMapPointDto] = []
        for territorial_code in territorial_codes:
            try:
                risk = self._predict_risk_use_case.execute(
                    PredictRiskQueryDto(territorial_code=territorial_code, period=query.period),
                )
            except EntityNotFoundError:
                continue
            latitude, longitude = resolve_territorial_coordinates(territorial_code)
            points.append(
                TerritorialRiskMapPointDto(
                    territorial_code=territorial_code,
                    municipality_name=_municipality_name(self._catalog, territorial_code),
                    period=query.period,
                    score=risk.score,
                    classification=risk.classification,
                    latitude=latitude,
                    longitude=longitude,
                )
            )
        return points


def _resolve_territories(query: TerritorialRiskMapQueryDto) -> tuple[str, ...]:
    if query.territorial_codes:
        codes = [code.strip() for code in query.territorial_codes.split(",") if code.strip()]
        return resolve_featured_territorial_codes(territorial_codes=codes, featured_only=False)
    if query.featured_only:
        return resolve_featured_territorial_codes(featured_only=True)
    return ()


def _municipality_name(catalog: DivipolaCatalog, territorial_code: str) -> str:
    name = catalog.municipality_name(territorial_code)
    return name.title() if name else territorial_code
