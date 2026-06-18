/** Etiquetas en español claro para la interfaz (no técnico). */

export const riskClassificationLabels: Record<string, string> = {
  low: "Bajo",
  medium: "Medio",
  high: "Alto",
  critical: "Muy alto",
};

export const severityLabels: Record<string, string> = {
  low: "Leve",
  medium: "Moderada",
  high: "Importante",
};

export const driftStatusLabels: Record<string, string> = {
  stable: "Sin cambios relevantes",
  warning: "Cambios moderados",
  alert: "Cambios importantes",
  unknown: "No disponible",
};

export const outbreakFeatureLabels: Record<string, string> = {
  cases_vs_median: "Casos vs mediana nacional",
  week_over_week_growth: "Crecimiento semanal",
  vaccination_gap: "Brecha de vacunación",
  health_access_gap: "Brecha de acceso a salud",
  pm25_exposure: "Exposición a PM2.5",
};

export function formatPeriodLabel(period: string): string {
  const weekMatch = /^(\d{4})-W(\d{2})$/.exec(period);
  if (weekMatch) {
    return `Semana epidemiológica ${Number(weekMatch[2])} de ${weekMatch[1]}`;
  }
  const match = /^(\d{4})-(\d{2})$/.exec(period);
  if (!match) return period;
  const year = match[1];
  const month = match[2];
  if (month === "01") {
    return `Año ${year}`;
  }
  return `${year}, mes ${month}`;
}

export function formatTerritoryLabel(code: string, name?: string | null): string {
  if (name) {
    return `${formatMunicipalityName(name)} (${code})`;
  }
  return `Municipio ${code}`;
}

export function formatMunicipalityName(name: string): string {
  return name
    .toLocaleLowerCase("es-CO")
    .replace(/(^|\s|['-])(\p{L})/gu, (match, prefix: string, letter: string) => {
      return `${prefix}${letter.toLocaleUpperCase("es-CO")}`;
    });
}
