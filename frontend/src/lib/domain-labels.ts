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

/** Factores del modelo de brotes (ML y reglas) en lenguaje claro. */
export const outbreakFeatureLabels: Record<string, string> = {
  log_observed_cases: "Volumen de casos observados",
  log_baseline_cases: "Referencia nacional de casos",
  cases_vs_median: "Casos vs mediana nacional",
  log_previous_week_cases: "Casos de la semana anterior",
  week_over_week_ratio: "Crecimiento respecto a la semana anterior",
  week_over_week_growth: "Crecimiento respecto a la semana anterior",
  vaccination_coverage_pct: "Cobertura de vacunación",
  vaccination_gap: "Brecha de vacunación",
  health_access_pct: "Acceso a servicios de salud",
  health_access_gap: "Brecha de acceso a salud",
  pm25_ug_m3: "Calidad del aire (PM2.5)",
  pm25_exposure: "Calidad del aire (PM2.5)",
  epidemiological_week_sin: "Estacionalidad del año",
  epidemiological_week_cos: "Ciclo epidemiológico anual",
  cases_above_baseline: "Por encima del promedio nacional",
  accelerated_growth: "Crecimiento acelerado de casos",
  territorial_risk_proxy: "Riesgo territorial combinado",
};

export const riskFeatureLabels: Record<string, string> = {
  neutral_baseline: "Línea base neutral",
  mortality_ratio_delta: "Diferencia respecto al promedio nacional",
  observed_mortality_rate: "Tasa de mortalidad observada",
};

const assumptionLabels: Record<string, string> = {
  "Outbreak probability predicted by a promoted Random Forest classifier.":
    "Probabilidad estimada con un modelo de bosques aleatorios entrenado con datos abiertos.",
  "Feature contributions computed with SHAP TreeExplainer.":
    "La explicación de cada factor usa SHAP (árboles de decisión).",
  "Model trained on multivariate datos.gov.co indicators with temporal validation.":
    "Entrenado con indicadores de datos.gov.co y validación temporal.",
  "Not validated for automatic public health activation.":
    "No sustituye la validación epidemiológica ni activa respuestas automáticas.",
  "Outbreak probability combines SIVIGILA case elevation, vaccination coverage, health access proxy and PM2.5 exposure.":
    "La señal combina casos SIVIGILA, vacunación, acceso a salud y calidad del aire (PM2.5).",
  "Weekly epidemiological periods use convention YYYY-Www.":
    "Los periodos siguen el formato de semana epidemiológica (año-semana).",
  "Vaccination coverage is expanded from departmental to municipal level.":
    "La cobertura de vacunación se estima por municipio a partir de datos departamentales.",
  "Score compares territorial general mortality to the national median for the same period.":
    "El puntaje compara la mortalidad del municipio con la mediana nacional del mismo periodo.",
  "Annual indicators use period convention YYYY-01.":
    "Los indicadores anuales usan el formato año-mes (YYYY-01).",
  "Not validated for operational public health decisions.":
    "No está validado para decisiones operativas de salud pública.",
};

const modelVersionLabels: Record<string, string> = {
  "randomforest-outbreak-v1.0.0": "Modelo de brotes — Bosques aleatorios v1.0.0",
  "outbreak-multivariate-v1.0.0": "Modelo de brotes basado en reglas v1.0.0",
  "ridge-mortality-risk-v1.0.0": "Modelo de riesgo territorial — Ridge v1.0.0",
  "mortality-relative-v1.0.0": "Riesgo territorial relativo v1.0.0",
  "prophet-annual-v1.0.0": "Proyección anual (Prophet) v1.0.0",
  "linear-extrapolation-v1.0.0": "Proyección lineal v1.0.0",
};

const driverPatterns: Array<{ pattern: RegExp; format: (match: RegExpMatchArray) => string }> = [
  {
    pattern: /^Observed (.+) cases: ([\d.]+)\.$/,
    format: (m) => `Casos de ${m[1]} observados: ${m[2]}.`,
  },
  {
    pattern: /^National median for period: ([\d.]+)\.$/,
    format: (m) => `Mediana nacional del periodo: ${m[1]}.`,
  },
  {
    pattern: /^Relative ratio vs median: ([\d.]+)\.$/,
    format: (m) => `Relación respecto a la mediana: ${m[1]}.`,
  },
  {
    pattern: /^Vaccination coverage: ([\d.]+)%\.$/,
    format: (m) => `Cobertura de vacunación: ${m[1]}%.`,
  },
  {
    pattern: /^Institutional births proxy: ([\d.]+)%\.$/,
    format: (m) => `Partos en institución de salud: ${m[1]}%.`,
  },
  {
    pattern: /^PM2\.5 annual mean: ([\d.]+) µg\/m³\.$/,
    format: (m) => `Promedio anual de PM2.5: ${m[1]} µg/m³.`,
  },
  {
    pattern: /^Observed general mortality rate: ([\d.]+) per 1000\.$/,
    format: (m) => `Tasa de mortalidad observada: ${m[1]} por cada 1.000 habitantes.`,
  },
  {
    pattern: /^National median for period: ([\d.]+) per 1000\.$/,
    format: (m) => `Mediana nacional del periodo: ${m[1]} por cada 1.000 habitantes.`,
  },
];

export function formatOutbreakFeatureLabel(feature: string): string {
  return outbreakFeatureLabels[feature] ?? humanizeTechnicalLabel(feature);
}

export function formatRiskFeatureLabel(feature: string): string {
  return riskFeatureLabels[feature] ?? humanizeTechnicalLabel(feature);
}

export function formatModelVersionLabel(version: string): string {
  return modelVersionLabels[version] ?? humanizeTechnicalLabel(version);
}

export function translateAssumption(text: string): string {
  return assumptionLabels[text] ?? text;
}

export function translateDriver(text: string): string {
  for (const { pattern, format } of driverPatterns) {
    const match = text.match(pattern);
    if (match) {
      return format(match);
    }
  }
  return text;
}

function humanizeTechnicalLabel(value: string): string {
  return value
    .replace(/_/g, " ")
    .replace(/\b(pct|ug|m3|wow|ml|rf)\b/gi, "")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/^\w/, (letter) => letter.toLocaleUpperCase("es-CO"));
}

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
