from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True, slots=True)
class TerritorialValidationSummary:
    accepted_count: int
    rejected_count: int
    rejected_territorial_codes: tuple[str, ...]


class TerritorialCatalog(Protocol):
    @property
    def source_id(self) -> str: ...

    @property
    def synced_at(self) -> str | None: ...

    @property
    def municipality_count(self) -> int: ...

    def is_valid_municipality(self, code: str) -> bool: ...


class DivipolaCatalog:
    """Static DANE DIVIPOLA municipality catalog bundled with the backend."""

    DEFAULT_PATH = (
        Path(__file__).resolve().parents[2] / "data" / "divipola_municipality_catalog.json"
    )

    def __init__(
        self,
        municipalities: dict[str, dict[str, str]],
        *,
        source_id: str,
        synced_at: str | None,
    ) -> None:
        self._municipalities = municipalities
        self._source_id = source_id
        self._synced_at = synced_at

    @classmethod
    def from_file(cls, path: Path | None = None) -> DivipolaCatalog:
        catalog_path = path or cls.DEFAULT_PATH
        payload = json.loads(catalog_path.read_text(encoding="utf-8"))
        municipalities = payload.get("municipalities", {})
        if not isinstance(municipalities, dict) or not municipalities:
            msg = f"DIVIPOLA catalog at {catalog_path} has no municipalities."
            raise ValueError(msg)
        return cls(
            municipalities=municipalities,
            source_id=str(payload.get("source_id", "dane-divipola")),
            synced_at=str(payload["synced_at"]) if payload.get("synced_at") else None,
        )

    @property
    def source_id(self) -> str:
        return self._source_id

    @property
    def synced_at(self) -> str | None:
        return self._synced_at

    @property
    def municipality_count(self) -> int:
        return len(self._municipalities)

    def is_valid_municipality(self, code: str) -> bool:
        normalized = code.strip().zfill(5) if code.strip().isdigit() else code.strip()
        return normalized in self._municipalities

    def municipality_name(self, code: str) -> str | None:
        entry = self._municipalities.get(code.strip().zfill(5))
        if entry is None:
            return None
        return str(entry.get("name", "")) or None

    def municipality_coordinates(self, code: str) -> tuple[float, float] | None:
        entry = self._municipalities.get(code.strip().zfill(5))
        if entry is None:
            return None
        latitude = entry.get("latitude")
        longitude = entry.get("longitude")
        if latitude is None or longitude is None:
            return None
        return float(latitude), float(longitude)
