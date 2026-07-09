/** Ciudades destacadas — alineadas con backend/shared/featured_municipalities.py */

export interface FeaturedMunicipalityOption {
  territorial_code: string;
  name: string;
  department_code: string;
  display_name: string;
}

export const PILOT_MUNICIPALITIES: FeaturedMunicipalityOption[] = [
  { territorial_code: "05001", name: "MEDELLÍN", department_code: "05", display_name: "Medellín" },
  { territorial_code: "11001", name: "BOGOTÁ, D.C.", department_code: "11", display_name: "Bogotá" },
  {
    territorial_code: "08001",
    name: "BARRANQUILLA",
    department_code: "08",
    display_name: "Barranquilla",
  },
  { territorial_code: "76001", name: "CALI", department_code: "76", display_name: "Cali" },
];

export const FEATURED_MUNICIPALITIES: FeaturedMunicipalityOption[] = [
  ...PILOT_MUNICIPALITIES,
  { territorial_code: "13001", name: "CARTAGENA DE INDIAS", department_code: "13", display_name: "Cartagena" },
  { territorial_code: "68001", name: "BUCARAMANGA", department_code: "68", display_name: "Bucaramanga" },
  { territorial_code: "54001", name: "CÚCUTA", department_code: "54", display_name: "Cúcuta" },
  { territorial_code: "66001", name: "PEREIRA", department_code: "66", display_name: "Pereira" },
  { territorial_code: "73001", name: "IBAGUÉ", department_code: "73", display_name: "Ibagué" },
  { territorial_code: "47001", name: "SANTA MARTA", department_code: "47", display_name: "Santa Marta" },
  { territorial_code: "63001", name: "ARMENIA", department_code: "63", display_name: "Armenia" },
  { territorial_code: "52001", name: "PASTO", department_code: "52", display_name: "Pasto" },
  { territorial_code: "17001", name: "MANIZALES", department_code: "17", display_name: "Manizales" },
  { territorial_code: "23001", name: "MONTERÍA", department_code: "23", display_name: "Montería" },
  { territorial_code: "41001", name: "NEIVA", department_code: "41", display_name: "Neiva" },
  { territorial_code: "19001", name: "POPAYÁN", department_code: "19", display_name: "Popayán" },
  { territorial_code: "15001", name: "TUNJA", department_code: "15", display_name: "Tunja" },
  { territorial_code: "50001", name: "VILLAVICENCIO", department_code: "50", display_name: "Villavicencio" },
  { territorial_code: "44001", name: "RIOHACHA", department_code: "44", display_name: "Riohacha" },
  { territorial_code: "20001", name: "VALLEDUPAR", department_code: "20", display_name: "Valledupar" },
];

export const DEFAULT_FEATURED_MUNICIPALITY = FEATURED_MUNICIPALITIES[0];

export const PILOT_MUNICIPALITY_CODES = PILOT_MUNICIPALITIES.map(
  (municipality) => municipality.territorial_code,
);

export const FEATURED_MUNICIPALITY_CODES = FEATURED_MUNICIPALITIES.map(
  (municipality) => municipality.territorial_code,
);
