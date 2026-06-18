/** Transmissible SIVIGILA events — aligned with backend/shared/sivigila_events.py */

export interface SivigilaEvent {
  code: string;
  definition_id: string;
  name: string;
  slug: string;
}

export const TRANSMISSIBLE_SIVIGILA_EVENTS: SivigilaEvent[] = [
  { code: "210", definition_id: "dengue-weekly-cases", name: "Dengue", slug: "dengue" },
  {
    code: "217",
    definition_id: "chikungunya-weekly-cases",
    name: "Chikungunya",
    slug: "chikungunya",
  },
  {
    code: "220",
    definition_id: "dengue-severe-weekly-cases",
    name: "Dengue grave",
    slug: "dengue-grave",
  },
  {
    code: "330",
    definition_id: "hepatitis-a-weekly-cases",
    name: "Hepatitis A",
    slug: "hepatitis-a",
  },
  {
    code: "340",
    definition_id: "hepatitis-b-weekly-cases",
    name: "Hepatitis B",
    slug: "hepatitis-b",
  },
  {
    code: "320",
    definition_id: "typhoid-weekly-cases",
    name: "Fiebre tifoidea",
    slug: "typhoid",
  },
];

export const DEFAULT_EVENT_CODE = "210";

export function resolveEventLabel(code: string): string {
  return TRANSMISSIBLE_SIVIGILA_EVENTS.find((event) => event.code === code)?.name ?? code;
}

export function resolveEventDefinitionId(code: string): string | undefined {
  return TRANSMISSIBLE_SIVIGILA_EVENTS.find((event) => event.code === code)?.definition_id;
}
