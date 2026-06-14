"""Tests for multi-year ingestion command resolution."""

from modules.epidemiological_surveillance.application.ingest_mortality_indicators import (
    _resolve_target_years,
)
from modules.epidemiological_surveillance.application.normalization import (
    IngestMortalityIndicatorsCommand,
)


def test_resolve_target_years_prefers_years_list() -> None:
    command = IngestMortalityIndicatorsCommand(
        source_id="datos-gov-mortality-indicators",
        definition_id="general-mortality-rate",
        source_indicator_key="TASA DE MORTALIDAD GENERAL",
        year=2020,
        years=(2018, 2019),
    )
    assert _resolve_target_years(command) == (2018, 2019)


def test_resolve_target_years_single_year() -> None:
    command = IngestMortalityIndicatorsCommand(
        source_id="datos-gov-mortality-indicators",
        definition_id="general-mortality-rate",
        source_indicator_key="TASA DE MORTALIDAD GENERAL",
        year=2020,
    )
    assert _resolve_target_years(command) == (2020,)
