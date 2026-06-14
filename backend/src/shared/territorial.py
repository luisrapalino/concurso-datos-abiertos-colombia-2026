from __future__ import annotations

import re

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema

_TERRITORIAL_CODE_PATTERN = re.compile(r"^\d{2,5}$")


class TerritorialCode(str):
    """Colombian DANE territorial code (department 2 digits, municipality up to 5)."""

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
    def _validate(cls, value: str) -> TerritorialCode:
        if not _TERRITORIAL_CODE_PATTERN.fullmatch(value):
            msg = "Territorial code must be 2 to 5 digits (DANE format)."
            raise ValueError(msg)
        return cls(value)
