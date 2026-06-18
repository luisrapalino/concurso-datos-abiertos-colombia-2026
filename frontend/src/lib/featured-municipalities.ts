/** Ciudades piloto — alineadas con backend/shared/featured_municipalities.py */

export interface FeaturedMunicipalityOption {
  territorial_code: string;
  name: string;
  department_code: string;
  display_name: string;
}

export const FEATURED_MUNICIPALITIES: FeaturedMunicipalityOption[] = [
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

export const DEFAULT_FEATURED_MUNICIPALITY = FEATURED_MUNICIPALITIES[0];

export const PILOT_MUNICIPALITY_CODES = FEATURED_MUNICIPALITIES.map(
  (municipality) => municipality.territorial_code,
);
