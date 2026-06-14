from __future__ import annotations

import re
from datetime import date

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema

_PERIOD_PATTERN = re.compile(r"^(?P<year>\d{4})-(?P<month>\d{2})$")


class Period(str):
    """Calendar month period in YYYY-MM format."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: type,
        _handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.str_schema(),
        )

    @classmethod
    def _validate(cls, value: str) -> Period:
        match = _PERIOD_PATTERN.fullmatch(value)
        if match is None:
            msg = "Period must use YYYY-MM format."
            raise ValueError(msg)

        year = int(match.group("year"))
        month = int(match.group("month"))
        if month < 1 or month > 12:
            msg = "Month must be between 01 and 12."
            raise ValueError(msg)

        date(year, month, 1)
        return cls(value)

    @property
    def year(self) -> int:
        return int(self[:4])

    @property
    def month(self) -> int:
        return int(self[5:7])
