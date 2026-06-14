import pytest
from pydantic import BaseModel, ValidationError

from shared.period import Period
from shared.territorial import TerritorialCode


class TerritorialCodeModel(BaseModel):
    code: TerritorialCode


class PeriodModel(BaseModel):
    period: Period


def test_territorial_code_accepts_dane_lengths() -> None:
    assert TerritorialCodeModel(code="05").code == "05"
    assert TerritorialCodeModel(code="05001").code == "05001"


def test_territorial_code_rejects_invalid_values() -> None:
    with pytest.raises(ValidationError):
        TerritorialCodeModel(code="abc")


def test_period_accepts_valid_month() -> None:
    period = PeriodModel(period="2024-06").period
    assert period.year == 2024
    assert period.month == 6


def test_period_rejects_invalid_month() -> None:
    with pytest.raises(ValidationError):
        PeriodModel(period="2024-13")
