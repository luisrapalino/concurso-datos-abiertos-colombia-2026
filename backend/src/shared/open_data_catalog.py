"""Enlaces y metadatos de conjuntos abiertos en datos.gov.co."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class OpenDataSourceMeta:
    source_id: str
    portal_url: str
    api_url: str
    provider: str


OPEN_DATA_SOURCES: dict[str, OpenDataSourceMeta] = {
    "datos-gov-sivigila": OpenDataSourceMeta(
        source_id="datos-gov-sivigila",
        portal_url=(
            "https://www.datos.gov.co/Salud-y-Protecci-n-Social/"
            "Datos-de-Vigilancia-en-Salud-P-blica-de-Colombia-SIVIGILA/4hyg-wa9d"
        ),
        api_url="https://www.datos.gov.co/resource/4hyg-wa9d.json",
        provider="INS · datos.gov.co",
    ),
    "datos-gov-vaccination-coverage": OpenDataSourceMeta(
        source_id="datos-gov-vaccination-coverage",
        portal_url=(
            "https://www.datos.gov.co/Salud-y-Protecci-n-Social/"
            "Coberturas-administrativas-de-vacunaci-n-por-departamento/6i25-2hdt"
        ),
        api_url="https://www.datos.gov.co/resource/6i25-2hdt.json",
        provider="MinSalud · datos.gov.co",
    ),
    "datos-gov-air-quality": OpenDataSourceMeta(
        source_id="datos-gov-air-quality",
        portal_url=(
            "https://www.datos.gov.co/Ambiente-y-Desarrollo-Sostenible/"
            "Calidad-del-Aire-en-Colombia-Promedio-Anual-/kekd-7v7h"
        ),
        api_url="https://www.datos.gov.co/resource/kekd-7v7h.json",
        provider="IDEAM / autoridades ambientales · datos.gov.co",
    ),
    "datos-gov-mortality-indicators": OpenDataSourceMeta(
        source_id="datos-gov-mortality-indicators",
        portal_url=(
            "https://www.datos.gov.co/Salud-y-Protecci-n-Social/"
            "Indicadores-mortalidad-y-morbilidad-seg-n-departam/4e4i-ua65"
        ),
        api_url="https://www.datos.gov.co/resource/4e4i-ua65.json",
        provider="INS · datos.gov.co",
    ),
}


def resolve_open_data_meta(source_id: str) -> OpenDataSourceMeta | None:
    return OPEN_DATA_SOURCES.get(source_id)
