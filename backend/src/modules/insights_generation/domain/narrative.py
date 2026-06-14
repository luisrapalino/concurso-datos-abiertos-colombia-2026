from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from modules.anomaly_detection.domain.detection import AnomalyAlert
from modules.territorial_risk.domain.risk_score import RiskClassification, RiskScore

INSIGHTS_VERSION = "composite-narrative-v1.0.0"
DATA_SOURCE_LABEL = "datos.gov.co — Indicadores mortalidad y morbilidad (INS, 4e4i-ua65)"


class InsightConfidence(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True, slots=True)
class TrendSummary:
    latest_period: str
    latest_value: float
    previous_value: float | None
    forecast_next_value: float | None
    historical_points: int


@dataclass(frozen=True, slots=True)
class TerritorialInsightContext:
    territorial_code: str
    indicator_name: str
    risk_score: RiskScore | None
    anomaly: AnomalyAlert | None
    trend: TrendSummary
    generated_at: datetime


@dataclass(frozen=True, slots=True)
class Insight:
    id: str
    territorial_code: str
    title: str
    narrative: str
    confidence: InsightConfidence
    data_version: str
    sources: tuple[str, ...]


def _risk_title(classification: RiskClassification) -> str:
    mapping = {
        RiskClassification.LOW: "Riesgo territorial bajo según mortalidad general",
        RiskClassification.MEDIUM: "Riesgo territorial moderado según mortalidad general",
        RiskClassification.HIGH: "Riesgo territorial elevado según mortalidad general",
        RiskClassification.CRITICAL: "Riesgo territorial crítico según mortalidad general",
    }
    return mapping[classification]


def _risk_confidence(classification: RiskClassification) -> InsightConfidence:
    if classification in {RiskClassification.HIGH, RiskClassification.CRITICAL}:
        return InsightConfidence.HIGH
    if classification == RiskClassification.MEDIUM:
        return InsightConfidence.MEDIUM
    return InsightConfidence.LOW


def generate_insights(context: TerritorialInsightContext) -> list[Insight]:
    insights: list[Insight] = []
    code = context.territorial_code

    if context.risk_score is not None:
        risk = context.risk_score
        insights.append(
            Insight(
                id=f"insight:{code}:risk:{risk.period}",
                territorial_code=code,
                title=_risk_title(risk.classification),
                narrative=(
                    f"En {risk.period}, la tasa de mortalidad general observada "
                    f"({risk.observed_value:.2f} por 1 000) se compara con una mediana "
                    f"nacional de {risk.baseline_value:.2f}. El score normalizado es "
                    f"{risk.score:.1f}/100 ({risk.classification.value}). "
                    "Este resultado requiere validación epidemiológica antes de cualquier "
                    "decisión operativa."
                ),
                confidence=_risk_confidence(risk.classification),
                data_version=INSIGHTS_VERSION,
                sources=(DATA_SOURCE_LABEL,),
            ),
        )

    if context.anomaly is not None:
        anomaly = context.anomaly
        insights.append(
            Insight(
                id=f"insight:{code}:{anomaly.id}",
                territorial_code=code,
                title="Anomalía detectada en mortalidad general",
                narrative=(
                    f"La observación del periodo {context.trend.latest_period} supera la "
                    f"mediana nacional (valor observado {anomaly.observed_value:.2f} vs "
                    f"baseline {anomaly.baseline_value:.2f}). Severidad: "
                    f"{anomaly.severity.value}. {anomaly.description}"
                ),
                confidence=InsightConfidence.HIGH
                if anomaly.severity.value == "high"
                else InsightConfidence.MEDIUM,
                data_version=INSIGHTS_VERSION,
                sources=(DATA_SOURCE_LABEL,),
            ),
        )

    trend = context.trend
    if trend.previous_value is not None:
        delta = trend.latest_value - trend.previous_value
        direction = "alza" if delta > 0 else "baja" if delta < 0 else "estabilidad"
        forecast_text = ""
        if trend.forecast_next_value is not None:
            forecast_text = (
                f" La proyección lineal para el siguiente periodo anual estima "
                f"{trend.forecast_next_value:.2f} por 1 000."
            )
        insights.append(
            Insight(
                id=f"insight:{code}:trend:{trend.latest_period}",
                territorial_code=code,
                title=f"Tendencia de {direction} en mortalidad general",
                narrative=(
                    f"La serie histórica ({trend.historical_points} periodos) muestra un "
                    f"cambio de {trend.previous_value:.2f} a {trend.latest_value:.2f} "
                    f"por 1 000 entre el penúltimo y el último periodo disponible "
                    f"({trend.latest_period}).{forecast_text} La proyección es exploratoria "
                    "y no sustituye modelos epidemiológicos calibrados."
                ),
                confidence=InsightConfidence.MEDIUM,
                data_version=INSIGHTS_VERSION,
                sources=(DATA_SOURCE_LABEL,),
            ),
        )

    insights.append(
        Insight(
            id=f"insight:{code}:coverage",
            territorial_code=code,
            title="Cobertura y límites de los datos",
            narrative=(
                f"Insight generado el {context.generated_at.date().isoformat()} con "
                f"{trend.historical_points} periodo(s) histórico(s) disponible(s) para "
                f"{context.indicator_name}. La plataforma no garantiza cobertura nacional "
                "completa ni validación clínica automática."
            ),
            confidence=InsightConfidence.LOW,
            data_version=INSIGHTS_VERSION,
            sources=(DATA_SOURCE_LABEL,),
        ),
    )

    return insights
