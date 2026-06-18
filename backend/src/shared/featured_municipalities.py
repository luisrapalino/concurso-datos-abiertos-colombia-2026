"""Curated pilot municipalities for the competition demo."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FeaturedMunicipality:
    territorial_code: str
    name: str
    department_code: str


PILOT_MUNICIPALITIES: tuple[FeaturedMunicipality, ...] = (
    FeaturedMunicipality("05001", "MEDELLÍN", "05"),
    FeaturedMunicipality("11001", "BOGOTÁ, D.C.", "11"),
    FeaturedMunicipality("08001", "BARRANQUILLA", "08"),
    FeaturedMunicipality("76001", "CALI", "76"),
)

# Alias kept for existing imports across modules and tests.
FEATURED_MUNICIPALITIES = PILOT_MUNICIPALITIES

FEATURED_MUNICIPALITY_CODES: tuple[str, ...] = tuple(
    municipality.territorial_code for municipality in PILOT_MUNICIPALITIES
)

PILOT_MUNICIPALITY_CODES = FEATURED_MUNICIPALITY_CODES

_FEATURED_CODE_SET = frozenset(FEATURED_MUNICIPALITY_CODES)


def is_featured_municipality(territorial_code: str) -> bool:
    return territorial_code.strip().zfill(5) in _FEATURED_CODE_SET


def resolve_featured_territorial_codes(
    *,
    territorial_codes: list[str] | None = None,
    featured_only: bool = True,
) -> tuple[str, ...]:
    if territorial_codes:
        normalized = tuple(code.strip().zfill(5) for code in territorial_codes if code.strip())
        return normalized or FEATURED_MUNICIPALITY_CODES
    if featured_only:
        return FEATURED_MUNICIPALITY_CODES
    return ()
