"""Curated municipalities for the competition demo and default ingestion."""

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

EXPANDED_MUNICIPALITIES: tuple[FeaturedMunicipality, ...] = PILOT_MUNICIPALITIES + (
    FeaturedMunicipality("13001", "CARTAGENA DE INDIAS", "13"),
    FeaturedMunicipality("68001", "BUCARAMANGA", "68"),
    FeaturedMunicipality("54001", "CÚCUTA", "54"),
    FeaturedMunicipality("66001", "PEREIRA", "66"),
    FeaturedMunicipality("73001", "IBAGUÉ", "73"),
    FeaturedMunicipality("47001", "SANTA MARTA", "47"),
    FeaturedMunicipality("63001", "ARMENIA", "63"),
    FeaturedMunicipality("52001", "PASTO", "52"),
    FeaturedMunicipality("17001", "MANIZALES", "17"),
    FeaturedMunicipality("23001", "MONTERÍA", "23"),
    FeaturedMunicipality("41001", "NEIVA", "41"),
    FeaturedMunicipality("19001", "POPAYÁN", "19"),
    FeaturedMunicipality("15001", "TUNJA", "15"),
    FeaturedMunicipality("50001", "VILLAVICENCIO", "50"),
    FeaturedMunicipality("44001", "RIOHACHA", "44"),
    FeaturedMunicipality("20001", "VALLEDUPAR", "20"),
)

# Default territorial scope for ingestion, mapas destacados y API featured_only.
FEATURED_MUNICIPALITIES = EXPANDED_MUNICIPALITIES

FEATURED_MUNICIPALITY_CODES: tuple[str, ...] = tuple(
    municipality.territorial_code for municipality in FEATURED_MUNICIPALITIES
)

PILOT_MUNICIPALITY_CODES: tuple[str, ...] = tuple(
    municipality.territorial_code for municipality in PILOT_MUNICIPALITIES
)

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
