from datetime import UTC, datetime

from modules.epidemiological_surveillance.application.get_data_drift import GetDataDriftUseCase
from modules.insights_generation.application.dto import ListInsightsQueryDto
from modules.insights_generation.application.generate_insights import GenerateInsightsUseCase
from modules.insights_generation.application.territorial_report_dto import (
    TerritorialReportQueryDto,
    TerritorialReportReadDto,
)
from modules.territorial_risk.application.dto import PredictRiskQueryDto
from modules.territorial_risk.application.predict_risk import PredictRiskUseCase


class GetTerritorialReportUseCase:
    """Composes a printable territorial intelligence report from existing analytics."""

    def __init__(
        self,
        predict_risk_use_case: PredictRiskUseCase,
        generate_insights_use_case: GenerateInsightsUseCase,
        get_data_drift_use_case: GetDataDriftUseCase,
    ) -> None:
        self._predict_risk = predict_risk_use_case
        self._generate_insights = generate_insights_use_case
        self._get_data_drift = get_data_drift_use_case

    def execute(self, query: TerritorialReportQueryDto) -> TerritorialReportReadDto:
        risk = self._predict_risk.execute(
            PredictRiskQueryDto(
                territorial_code=query.territorial_code,
                period=query.period,
            ),
        )
        insights = self._generate_insights.execute(
            ListInsightsQueryDto(
                territorial_code=query.territorial_code,
                limit=query.insight_limit,
            ),
        )
        drift = self._get_data_drift.execute()

        return TerritorialReportReadDto(
            territorial_code=query.territorial_code,
            period=query.period,
            generated_at=datetime.now(tz=UTC),
            risk=risk,
            insights=insights,
            drift_status=drift.drift_status,
            drift_note=drift.drift_note,
        )
