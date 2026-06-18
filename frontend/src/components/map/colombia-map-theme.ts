import type { LatLngBoundsExpression } from "leaflet";

/** Límites aproximados de Colombia (sur-oeste → norte-este). */
export const COLOMBIA_BOUNDS: LatLngBoundsExpression = [
  [-4.5, -81.8],
  [13.6, -66.5],
];

export const COLOMBIA_CENTER: [number, number] = [4.6, -74.1];

export const mapThemeLight = {
  background: "#b8cdc6",
  landFill: "#fafcfb",
  landStroke: "#3d6b62",
  landWeight: 1.5,
  markerStroke: "#fafcfb",
  markerStrokeWidth: 2.5,
  selectedRing: "#0a5c54",
} as const;

export const mapThemeDark = {
  background: "#0f2420",
  landFill: "#1a3530",
  landStroke: "#5eead4",
  landWeight: 1.5,
  markerStroke: "#142824",
  markerStrokeWidth: 2.5,
  selectedRing: "#2dd4bf",
} as const;

/** @deprecated Usa useMapTheme() en componentes cliente */
export const mapTheme = mapThemeLight;

export const classificationColors = {
  low: "#0a5c54",
  medium: "#b45309",
  high: "#b42318",
  critical: "#7f1d1d",
} as const;

export const classificationColorsDark = {
  low: "#2dd4bf",
  medium: "#fbbf24",
  high: "#f87171",
  critical: "#fca5a5",
} as const;

export type MapClassification = keyof typeof classificationColors;
