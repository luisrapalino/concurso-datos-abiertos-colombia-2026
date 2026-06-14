import type {
  AnomalyAlertPage,
  DataDrift,
  DataFreshness,
  GeoFeatureCollection,
  HealthIndicator,
  Insight,
  RiskScore,
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

function normalizeRiskScore(payload: RiskScore): RiskScore {
  return {
    ...payload,
    drivers: payload.drivers ?? [],
    assumptions: payload.assumptions ?? [],
    feature_contributions: payload.feature_contributions ?? [],
    persisted: payload.persisted ?? false,
  };
}

function normalizeTerritorialTrend(payload: TerritorialTrend): TerritorialTrend {
  return {
    ...payload,
    assumptions: payload.assumptions ?? [],
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

  listTerritorialRiskMap(params: { period: string; limit?: number }) {
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
};
