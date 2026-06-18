"""SIVIGILA transmissible disease events ingested from datos.gov.co (4hyg-wa9d)."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SivigilaEvent:
    code: str
    definition_id: str
    name: str
    slug: str


TRANSMISSIBLE_SIVIGILA_EVENTS: tuple[SivigilaEvent, ...] = (
    SivigilaEvent("210", "dengue-weekly-cases", "DENGUE", "dengue"),
    SivigilaEvent("217", "chikungunya-weekly-cases", "CHIKUNGUNYA", "chikungunya"),
    SivigilaEvent("220", "dengue-severe-weekly-cases", "DENGUE GRAVE", "dengue-grave"),
    SivigilaEvent("330", "hepatitis-a-weekly-cases", "HEPATITIS A", "hepatitis-a"),
    SivigilaEvent("340", "hepatitis-b-weekly-cases", "HEPATITIS B", "hepatitis-b"),
    SivigilaEvent("320", "typhoid-weekly-cases", "FIEBRE TIFOIDEA Y PARATIFOIDEA", "typhoid"),
)

_SIVIGILA_BY_CODE = {event.code: event for event in TRANSMISSIBLE_SIVIGILA_EVENTS}
_SIVIGILA_BY_DEFINITION = {event.definition_id: event for event in TRANSMISSIBLE_SIVIGILA_EVENTS}


def resolve_sivigila_event(event_code: str) -> SivigilaEvent | None:
    return _SIVIGILA_BY_CODE.get(event_code.strip())


def resolve_sivigila_event_by_definition(definition_id: str) -> SivigilaEvent | None:
    return _SIVIGILA_BY_DEFINITION.get(definition_id)


def sivigila_definition_ids() -> tuple[str, ...]:
    return tuple(event.definition_id for event in TRANSMISSIBLE_SIVIGILA_EVENTS)
