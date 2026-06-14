from modules.insights_generation.application.dto import (
    InsightConfidence,
    InsightReadDto,
    ListInsightsQueryDto,
)


class GenerateInsightsUseCase:
    """Returns stub narrative insights until real generation pipelines exist."""

    _DATA_VERSION = "stub-dataset-v0.1.0"
    _SOURCES = ("SIVIGILA (placeholder)", "DANE open data (placeholder)")

    def execute(self, query: ListInsightsQueryDto) -> list[InsightReadDto]:
        insights = [
            InsightReadDto(
                id=f"stub-insight-{query.territorial_code}-001",
                territorial_code=query.territorial_code,
                title="Elevated mortality trend under manual review",
                narrative=(
                    "The territorial mortality indicator shows a sustained increase over the "
                    "last six periods compared with the rolling baseline. This insight is "
                    "generated from stub data and requires epidemiological validation before "
                    "operational use."
                ),
                confidence=InsightConfidence.MEDIUM,
                data_version=self._DATA_VERSION,
                sources=list(self._SOURCES),
            ),
            InsightReadDto(
                id=f"stub-insight-{query.territorial_code}-002",
                territorial_code=query.territorial_code,
                title="Forecast suggests stabilization in the short term",
                narrative=(
                    "Short-horizon projections indicate a possible plateau in the selected "
                    "indicator. Uncertainty remains high due to limited historical coverage in "
                    "the MVP dataset."
                ),
                confidence=InsightConfidence.LOW,
                data_version=self._DATA_VERSION,
                sources=list(self._SOURCES),
            ),
        ]
        return insights[: query.limit]
