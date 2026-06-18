"""Catalog of open-data dataset candidates per health indicator variable.

For each municipality the resolver tries bindings in ascending ``priority`` order
and uses the first dataset that returns observations for the requested period.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from shared.sivigila_events import TRANSMISSIBLE_SIVIGILA_EVENTS, sivigila_definition_ids

ClientType = Literal[
    "mortality",
    "sivigila",
    "vaccination",
    "air_quality_annual",
    "air_quality_sisaire",
]

SOURCE_MORTALITY = "datos-gov-mortality-indicators"
SOURCE_SIVIGILA = "datos-gov-sivigila"
SOURCE_VACCINATION = "datos-gov-vaccination-coverage"
SOURCE_AIR_QUALITY = "datos-gov-air-quality"

API_MORTALITY = "https://www.datos.gov.co/resource/4e4i-ua65.json"
API_SIVIGILA = "https://www.datos.gov.co/resource/4hyg-wa9d.json"
API_VACCINATION = "https://www.datos.gov.co/resource/6i25-2hdt.json"
API_AIR_ANNUAL = "https://www.datos.gov.co/resource/kekd-7v7h.json"
API_AIR_SISAIRE = "https://www.datos.gov.co/resource/yspz-pxxn.json"

PORTAL_MORTALITY = (
    "https://www.datos.gov.co/Salud-y-Protecci-n-Social/"
    "Indicadores-mortalidad-y-morbilidad-seg-n-departam/4e4i-ua65"
)
PORTAL_SIVIGILA = (
    "https://www.datos.gov.co/Salud-y-Protecci-n-Social/"
    "Datos-de-Vigilancia-en-Salud-P-blica-de-Colombia-SIVIGILA/4hyg-wa9d"
)
PORTAL_VACCINATION = (
    "https://www.datos.gov.co/Salud-y-Protecci-n-Social/"
    "Coberturas-administrativas-de-vacunaci-n-por-departamento/6i25-2hdt"
)
PORTAL_AIR_ANNUAL = (
    "https://www.datos.gov.co/Ambiente-y-Desarrollo-Sostenible/"
    "Calidad-del-Aire-en-Colombia-Promedio-Anual-/kekd-7v7h"
)
PORTAL_AIR_SISAIRE = (
    "https://www.datos.gov.co/Ambiente-y-Desarrollo-Sostenible/"
    "Sistema-de-Informaci-n-sobre-Calidad-del-Aire-PM10-y-PM2-5-SISAIRE/yspz-pxxn"
)

DEFINITION_GENERAL_MORTALITY = "general-mortality-rate"
DEFINITION_INSTITUTIONAL_BIRTHS = "institutional-births-coverage"
DEFINITION_VACCINATION = "dpta-penta-vaccination-coverage"
DEFINITION_PM25 = "pm25-annual-mean"

GENERAL_MORTALITY_INDICATOR = "TASA DE MORTALIDAD GENERAL"
INSTITUTIONAL_BIRTHS_INDICATOR = "PORCENTAJE DE PARTOS INSTITUCIONALES"
PENTAVALENT_VACCINE_KEY = "PENTA3"


@dataclass(frozen=True, slots=True)
class MunicipalDatasetBinding:
    binding_id: str
    source_id: str
    api_url: str
    portal_url: str
    provider: str
    client_type: ClientType
    source_indicator_key: str
    granularity: str
    priority: int
    selection_note: str


VARIABLE_DISPLAY_NAMES: dict[str, str] = {
    DEFINITION_GENERAL_MORTALITY: "Tasa de mortalidad general",
    DEFINITION_INSTITUTIONAL_BIRTHS: "Partos institucionales (proxy acceso)",
    DEFINITION_VACCINATION: "Cobertura vacunal pentavalente",
    DEFINITION_PM25: "PM2.5 promedio anual",
    **{event.definition_id: f"Casos semanales — {event.name.title()}" for event in TRANSMISSIBLE_SIVIGILA_EVENTS},
}

COMPETITION_DEFINITION_IDS: tuple[str, ...] = (
    *sivigila_definition_ids(),
    DEFINITION_VACCINATION,
    DEFINITION_PM25,
    DEFINITION_INSTITUTIONAL_BIRTHS,
    DEFINITION_GENERAL_MORTALITY,
)


def _mortality_binding(indicator_key: str, definition_id: str) -> MunicipalDatasetBinding:
    return MunicipalDatasetBinding(
        binding_id=f"mortality-{definition_id}",
        source_id=SOURCE_MORTALITY,
        api_url=API_MORTALITY,
        portal_url=PORTAL_MORTALITY,
        provider="INS · datos.gov.co",
        client_type="mortality",
        source_indicator_key=indicator_key,
        granularity="municipality-annual",
        priority=1,
        selection_note="Indicador municipal anual filtrado por codmunicipio",
    )


def _sivigila_binding(event_code: str, definition_id: str) -> MunicipalDatasetBinding:
    return MunicipalDatasetBinding(
        binding_id=f"sivigila-{definition_id}",
        source_id=SOURCE_SIVIGILA,
        api_url=API_SIVIGILA,
        portal_url=PORTAL_SIVIGILA,
        provider="INS · datos.gov.co",
        client_type="sivigila",
        source_indicator_key=event_code,
        granularity="municipality-weekly",
        priority=1,
        selection_note="Casos semanales SIVIGILA filtrados por cod_mun_o",
    )


MUNICIPAL_DATASET_BINDINGS: dict[str, tuple[MunicipalDatasetBinding, ...]] = {
    DEFINITION_GENERAL_MORTALITY: (
        _mortality_binding(GENERAL_MORTALITY_INDICATOR, DEFINITION_GENERAL_MORTALITY),
    ),
    DEFINITION_INSTITUTIONAL_BIRTHS: (
        _mortality_binding(INSTITUTIONAL_BIRTHS_INDICATOR, DEFINITION_INSTITUTIONAL_BIRTHS),
    ),
    DEFINITION_VACCINATION: (
        MunicipalDatasetBinding(
            binding_id="vaccination-dept-coverage",
            source_id=SOURCE_VACCINATION,
            api_url=API_VACCINATION,
            portal_url=PORTAL_VACCINATION,
            provider="MinSalud · datos.gov.co",
            client_type="vaccination",
            source_indicator_key=PENTAVALENT_VACCINE_KEY,
            granularity="department-annual-expanded",
            priority=1,
            selection_note="Cobertura departamental replicada al municipio piloto",
        ),
    ),
    DEFINITION_PM25: (
        MunicipalDatasetBinding(
            binding_id="pm25-annual-municipal",
            source_id=SOURCE_AIR_QUALITY,
            api_url=API_AIR_ANNUAL,
            portal_url=PORTAL_AIR_ANNUAL,
            provider="IDEAM / autoridades ambientales · datos.gov.co",
            client_type="air_quality_annual",
            source_indicator_key="pm25",
            granularity="municipality-annual",
            priority=1,
            selection_note="Promedio anual municipal (estaciones agregadas por municipio)",
        ),
        MunicipalDatasetBinding(
            binding_id="pm25-sisaire-daily",
            source_id=SOURCE_AIR_QUALITY,
            api_url=API_AIR_SISAIRE,
            portal_url=PORTAL_AIR_SISAIRE,
            provider="IDEAM · datos.gov.co",
            client_type="air_quality_sisaire",
            source_indicator_key="pm25",
            granularity="station-daily-aggregated",
            priority=2,
            selection_note="Respaldo SISAIRE: lecturas diarias por estación del municipio",
        ),
    ),
}

for _event in TRANSMISSIBLE_SIVIGILA_EVENTS:
    MUNICIPAL_DATASET_BINDINGS[_event.definition_id] = (
        _sivigila_binding(_event.code, _event.definition_id),
    )


def list_bindings_for_definition(definition_id: str) -> tuple[MunicipalDatasetBinding, ...]:
    bindings = MUNICIPAL_DATASET_BINDINGS.get(definition_id)
    if bindings is None:
        return ()
    return tuple(sorted(bindings, key=lambda item: item.priority))


def variable_display_name(definition_id: str) -> str:
    return VARIABLE_DISPLAY_NAMES.get(definition_id, definition_id)
