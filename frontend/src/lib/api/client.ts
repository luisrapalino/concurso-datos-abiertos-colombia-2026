import type {
  AnomalyAlertPage,
  HealthIndicator,
  Insight,
  RiskScore,
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
    return fetchJson<RiskScore>(buildApiUrl("/predict-risk", params));
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
    );
  },

  listInsights(params: { territorial_code: string; limit?: number }) {
    return fetchJson<Insight[]>(buildApiUrl("/insights", params));
  },
};
