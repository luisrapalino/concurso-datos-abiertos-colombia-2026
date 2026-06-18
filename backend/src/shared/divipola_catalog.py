from __future__ import annotations

import json
import unicodedata
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

    def get_municipality(self, code: str) -> dict[str, str] | None:
        return self._municipalities.get(code.strip().zfill(5))

    def search_municipalities(self, query: str, *, limit: int = 10) -> list[dict[str, str]]:
        normalized_query = _normalize_search_text(query)
        if not normalized_query:
            return []

        if normalized_query.isdigit():
            code = normalized_query.zfill(5)
            entry = self._municipalities.get(code)
            if entry is not None:
                return [_municipality_record(code, entry)]
            return []

        if len(normalized_query) < 2:
            return []

        matches: list[tuple[int, str, dict[str, str]]] = []
        for code, entry in self._municipalities.items():
            name = _normalize_search_text(str(entry.get("name", "")))
            if normalized_query not in name:
                continue
            rank = 0 if name.startswith(normalized_query) else 1
            matches.append((rank, str(entry.get("name", "")), _municipality_record(code, entry)))

        matches.sort(key=lambda item: (item[0], item[1]))
        return [item[2] for item in matches[:limit]]

    def municipality_codes_for_department(self, department_code: str) -> tuple[str, ...]:
        normalized_department = department_code.strip().zfill(2)
        return tuple(
            code
            for code, entry in self._municipalities.items()
            if str(entry.get("department_code", "")).zfill(2) == normalized_department
        )

    def all_municipality_codes(self) -> tuple[str, ...]:
        return tuple(sorted(self._municipalities.keys()))

    def resolve_municipality_by_name(self, name: str) -> str | None:
        normalized_name = _normalize_search_text(name)
        if not normalized_name:
            return None

        exact_matches = [
            code
            for code, entry in self._municipalities.items()
            if _normalize_search_text(str(entry.get("name", ""))) == normalized_name
        ]
        if len(exact_matches) == 1:
            return exact_matches[0]

        partial_matches = [
            code
            for code, entry in self._municipalities.items()
            if normalized_name in _normalize_search_text(str(entry.get("name", "")))
        ]
        if len(partial_matches) == 1:
            return partial_matches[0]
        return None


def _normalize_search_text(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value.strip())
    without_accents = "".join(
        character for character in normalized if unicodedata.category(character) != "Mn"
    )
    return without_accents.casefold()


def _municipality_record(code: str, entry: dict[str, str]) -> dict[str, str]:
    name = str(entry.get("name", ""))
    department_code = str(entry.get("department_code", ""))
    return {
        "territorial_code": code,
        "name": name,
        "department_code": department_code,
        "display_name": f"{name.title()} ({code})",
    }
