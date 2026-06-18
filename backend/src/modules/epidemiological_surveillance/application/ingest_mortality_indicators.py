from modules.epidemiological_surveillance.application.ingest_health_indicators import (
    IngestHealthIndicatorsUseCase,
)
from modules.epidemiological_surveillance.application.normalization import (
    IngestHealthIndicatorsCommand,
    IngestMortalityIndicatorsCommand,
)

IngestMortalityIndicatorsUseCase = IngestHealthIndicatorsUseCase

__all__ = [
    "IngestHealthIndicatorsCommand",
    "IngestHealthIndicatorsUseCase",
    "IngestMortalityIndicatorsCommand",
    "IngestMortalityIndicatorsUseCase",
]
