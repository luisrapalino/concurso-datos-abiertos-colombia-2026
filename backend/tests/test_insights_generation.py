from decimal import Decimal

from modules.anomaly_detection.domain.detection import ObservationWithBaseline
from modules.anomaly_detection.domain.repositories import TerritorialSeriesPoint
from modules.insights_generation.application.dto import ListInsightsQueryDto
from modules.insights_generation.application.generate_insights import GenerateInsightsUseCase
from modules.insights_generation.domain.narrative import INSIGHTS_VERSION
from modules.territorial_risk.domain.risk_score import MortalityObservation


class FakeInsightsReader:
    def list_observations_with_period_median(
        self,
        definition_id: str,
        *,
        territorial_code: str | None = None,
    ) -> list[ObservationWithBaseline]:
        del definition_id
        if territorial_code != "05001":
            return []
        return [
            ObservationWithBaseline(
                territorial_code="05001",
                period="2020-01",
                value=Decimal("16.0"),
                baseline=Decimal("8.0"),
                definition_id="general-mortality-rate",
                definition_name="Tasa de mortalidad general",
            ),
        ]

    def list_territorial_series(
        self,
        territorial_code: str,
        definition_id: str,
    ) -> tuple[str, list[TerritorialSeriesPoint]]:
        del definition_id
        if territorial_code != "05001":
            return "Tasa de mortalidad general", []
        return "Tasa de mortalidad general", [
            TerritorialSeriesPoint(period="2019-01", value=Decimal("7.0")),
            TerritorialSeriesPoint(period="2020-01", value=Decimal("16.0")),
        ]


class FakeRiskDataPort:
    def get_mortality_observation(
        self,
        territorial_code: str,
        period: str,
    ) -> MortalityObservation | None:
        if territorial_code == "05001" and period == "2020-01":
            return MortalityObservation(
                definition_id="general-mortality-rate",
                territorial_code="05001",
                period="2020-01",
                value=Decimal("16.0"),
            )
        return None

    def get_national_median_mortality(self, period: str) -> Decimal | None:
        if period == "2020-01":
            return Decimal("8.0")
        return None

    def list_territorial_codes_for_period(
        self,
        period: str,
        *,
        definition_id: str = "general-mortality-rate",
        limit: int = 500,
    ) -> list[str]:
        del period, definition_id, limit
        return ["05001"]


def test_generate_insights_use_case_respects_limit() -> None:
    insights = GenerateInsightsUseCase(
        FakeInsightsReader(),
        FakeRiskDataPort(),
    ).execute(ListInsightsQueryDto(territorial_code="05001", limit=2))
    assert len(insights) == 2
    assert insights[0].data_version == INSIGHTS_VERSION
    assert insights[0].sources
    assert insights[0].system_context
