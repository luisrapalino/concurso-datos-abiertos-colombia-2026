/** Límites aproximados de Colombia para ECharts geo (oeste-norte → este-sur). */
export const COLOMBIA_BOUNDS_GEO: [[number, number], [number, number]] = [
  [-81.8, 13.6],
  [-66.5, -4.5],
];

export const COLOMBIA_MAP_NAME = "colombia-departments";

export const mapThemeLight = {
  background: "#b8cdc6",
  landFill: "#fafcfb",
  landStroke: "#3d6b62",
  landWeight: 1.5,
  markerStroke: "#fafcfb",
  markerStrokeWidth: 2.5,
  selectedRing: "#0a5c54",
  tooltipBg: "#fafcfb",
  tooltipBorder: "#c8d9d4",
  tooltipText: "#142824",
  tooltipMuted: "#5c6f6b",
} as const;

export const mapThemeDark = {
  background: "#0f2420",
  landFill: "#1a3530",
  landStroke: "#5eead4",
  landWeight: 1.5,
  markerStroke: "#142824",
  markerStrokeWidth: 2.5,
  selectedRing: "#2dd4bf",
  tooltipBg: "#142824",
  tooltipBorder: "#1f3d37",
  tooltipText: "#e8f5f1",
  tooltipMuted: "#94b8ad",
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
