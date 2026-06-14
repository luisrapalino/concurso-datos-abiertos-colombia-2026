from decimal import Decimal

from modules.epidemiological_surveillance.application.normalization import (
    annual_period,
    normalize_indicator_value,
    normalize_territorial_code,
    observation_id,
)


def test_normalize_territorial_code_zero_pads_municipality() -> None:
    assert normalize_territorial_code("5001") == "05001"


def test_annual_period_uses_january_convention() -> None:
    assert annual_period(2023) == "2023-01"


def test_observation_id_is_deterministic() -> None:
    assert observation_id("general-mortality-rate", "05001", "2023-01") == (
        "general-mortality-rate:05001:2023-01"
    )


def test_normalize_indicator_value_parses_decimal() -> None:
    assert normalize_indicator_value("6.305277865") == Decimal("6.305277865")
