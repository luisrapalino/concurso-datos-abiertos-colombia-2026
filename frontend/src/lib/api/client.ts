import {
  formatOutbreakFeatureLabel,
  formatRiskFeatureLabel,
  translateAssumption,
  translateDriver,
} from "@/lib/domain-labels";
import type {
  AnomalyAlertPage,
  BiasAnalysis,
  DataDrift,
  DataFreshness,
  DatasetCatalogEntry,
  MunicipalVariableDataset,
  GeoFeatureCollection,
  HealthIndicator,
  Insight,
  Municipality,
  OutbreakAlert,
  OutbreakMapPoint,
  OutbreakPrediction,
  RiskScore,
  TerritorialReport,
  TerritorialRiskMapPoint,
  TerritorialTrend,
} from "@/lib/api/types";

type QueryValue = string | number | boolean | null | undefined;

function buildApiUrl(path: string, params?: Record<string, QueryValue>): string {
  const searchParams = new URLSearchParams();

  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (value !== null && value !== undefined && value !== "") {
        searchParams.set(key, String(value));
      }
    }
  }

  const query = searchParams.toString();
  const suffix = query ? `?${query}` : "";

  if (typeof window !== "undefined") {
    return `/api/v1${path}${suffix}`;
  }

  const origin =
    process.env.API_INTERNAL_URL ??
    process.env.NEXT_PUBLIC_API_URL ??
    "http://localhost:8000";

  return `${origin}/api/v1${path}${suffix}`;
}

async function fetchJson<T>(url: string): Promise<T> {
  const response = await fetch(url, {
    headers: { Accept: "application/json" },
    cache: "no-store",
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Error HTTP ${response.status}`);
  }

  return response.json() as Promise<T>;
}

function normalizeOutbreakPrediction(payload: OutbreakPrediction): OutbreakPrediction {
  return {
    ...payload,
    drivers: (payload.drivers ?? []).map(translateDriver),
    assumptions: (payload.assumptions ?? []).map(translateAssumption),
    feature_contributions: (payload.feature_contributions ?? []).map((item) => ({
      ...item,
      feature: formatOutbreakFeatureLabel(item.feature),
    })),
    persisted: payload.persisted ?? false,
  };
}

function normalizeRiskScore(payload: RiskScore): RiskScore {
  return {
    ...payload,
    drivers: (payload.drivers ?? []).map(translateDriver),
    assumptions: (payload.assumptions ?? []).map(translateAssumption),
    feature_contributions: (payload.feature_contributions ?? []).map((item) => ({
      ...item,
      feature: formatRiskFeatureLabel(item.feature),
    })),
    persisted: payload.persisted ?? false,
  };
}

function normalizeTerritorialTrend(payload: TerritorialTrend): TerritorialTrend {
  return {
    ...payload,
    assumptions: (payload.assumptions ?? []).map(translateAssumption),
    points: payload.points ?? [],
  };
}

export const epidemiologicalApi = {
  listHealthIndicators(params?: {
    territorial_code?: string;
    period?: string;
    definition_id?: string;
    limit?: number;
  }) {
    return fetchJson<HealthIndicator[]>(
      buildApiUrl("/health-indicators", params),
    );
  },

  listOutbreakAlerts(params: {
    period: string;
    event_code?: string;
    all_events?: boolean;
    featured_only?: boolean;
    territorial_codes?: string;
    limit?: number;
  }) {
    return fetchJson<OutbreakAlert[]>(buildApiUrl("/outbreak-alerts", params));
  },

  predictOutbreak(params: {
    territorial_code: string;
    period: string;
    event_code?: string;
  }) {
    return fetchJson<OutbreakPrediction>(
      buildApiUrl("/outbreak-predictions", params),
    ).then(normalizeOutbreakPrediction);
  },

  listOutbreakMap(params: {
    period: string;
    event_code?: string;
    featured_only?: boolean;
    limit?: number;
  }) {
    return fetchJson<OutbreakMapPoint[]>(buildApiUrl("/outbreak-map", params));
  },

  predictRisk(params: { territorial_code: string; period: string }) {
    return fetchJson<RiskScore>(buildApiUrl("/predict-risk", params)).then(
      normalizeRiskScore,
    );
  },

  listAnomalies(params?: {
    territorial_code?: string;
    page?: number;
    page_size?: number;
  }) {
    return fetchJson<AnomalyAlertPage>(buildApiUrl("/anomalies", params));
  },

  getTerritorialTrends(params: {
    territorial_code: string;
    indicator_id?: string;
    horizon_weeks?: number;
  }) {
    return fetchJson<TerritorialTrend>(
      buildApiUrl("/territorial-trends", params),
    ).then(normalizeTerritorialTrend);
  },

  listInsights(params: { territorial_code: string; limit?: number }) {
    return fetchJson<Insight[]>(buildApiUrl("/insights", params));
  },

  getDataFreshness(sourceId = "datos-gov-mortality-indicators") {
    return fetchJson<DataFreshness>(
      buildApiUrl("/data-freshness", { source_id: sourceId }),
    );
  },

  listDatasets() {
    return fetchJson<DatasetCatalogEntry[]>(buildApiUrl("/datasets"));
  },

  listMunicipalVariableDatasets() {
    return fetchJson<MunicipalVariableDataset[]>(buildApiUrl("/municipal-datasets"));
  },

  listTerritorialRiskMap(params: {
    period: string;
    featured_only?: boolean;
    limit?: number;
  }) {
    return fetchJson<TerritorialRiskMapPoint[]>(
      buildApiUrl("/territorial-risk-map", params),
    );
  },

  getTerritorialBoundaries(level = "department") {
    return fetchJson<GeoFeatureCollection>(
      buildApiUrl("/territorial-boundaries", { level }),
    );
  },

  getDataDrift(definitionId = "general-mortality-rate") {
    return fetchJson<DataDrift>(
      buildApiUrl("/data-drift", { definition_id: definitionId }),
    );
  },

  getTerritorialReport(params: {
    territorial_code: string;
    period: string;
    insight_limit?: number;
  }) {
    return fetchJson<TerritorialReport>(buildApiUrl("/territorial-report", params)).then(
      (payload) => ({
        ...payload,
        risk: normalizeRiskScore(payload.risk),
      }),
    );
  },

  getBiasAnalysis(params: { period: string; definition_id?: string }) {
    return fetchJson<BiasAnalysis>(buildApiUrl("/bias-analysis", params));
  },

  searchMunicipalities(params: { search: string; limit?: number }) {
    return fetchJson<Municipality[]>(buildApiUrl("/municipalities", params));
  },

  listFeaturedMunicipalities() {
    return fetchJson<Municipality[]>(buildApiUrl("/municipalities/featured"));
  },

  getMunicipality(territorialCode: string) {
    return fetchJson<Municipality>(buildApiUrl(`/municipalities/${territorialCode}`));
  },
};
