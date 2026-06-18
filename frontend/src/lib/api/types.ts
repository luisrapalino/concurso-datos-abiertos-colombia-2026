export type RiskClassification = "low" | "medium" | "high" | "critical";
export type AnomalySeverity = "low" | "medium" | "high";
export type TrendPointKind = "historical" | "forecast";
export type InsightConfidence = "low" | "medium" | "high";

export interface OutbreakPrediction {
  territorial_code: string;
  period: string;
  event_code: string;
  event_name: string;
  outbreak_probability: number;
  classification: RiskClassification;
  model_version: string;
  observed_cases: number;
  baseline_cases: number;
  assumptions: string[];
  drivers: string[];
  feature_contributions: OutbreakFeatureContribution[];
  generated_at: string;
  persisted: boolean;
}

export interface OutbreakFeatureContribution {
  feature: string;
  contribution: number;
  direction: string;
}

export interface OutbreakMapPoint {
  territorial_code: string;
  municipality_name: string;
  period: string;
  event_name: string;
  outbreak_probability: number;
  classification: RiskClassification;
  observed_cases: number;
  latitude: number;
  longitude: number;
}

export interface OutbreakAlert {
  territorial_code: string;
  municipality_name: string;
  period: string;
  event_code: string;
  event_name: string;
  outbreak_probability: number;
  classification: RiskClassification;
  observed_cases: number;
  baseline_cases: number;
  top_driver: string | null;
}

export interface FeatureContribution {
  feature: string;
  value: number;
  contribution: number;
  description: string;
}

export interface DataFreshness {
  source_id: string;
  source_name: string;
  last_successful_ingestion_at: string | null;
  records_upserted: number | null;
  latest_period_available: string | null;
  coverage_note: string;
}

export interface DatasetCatalogEntry {
  definition_id: string;
  name: string;
  source_id: string;
  source_name: string;
  provider: string;
  portal_url: string;
  api_url: string;
  measurement_unit: string;
  granularity: string;
  records_ingested: number;
  municipalities_count: number;
  latest_period: string | null;
  last_ingestion_at: string | null;
  coverage_note: string;
}

export interface MunicipalVariableDataset {
  territorial_code: string;
  municipality_name: string;
  definition_id: string;
  variable_name: string;
  active_binding_id: string;
  source_id: string;
  api_url: string;
  portal_url: string;
  provider: string;
  granularity: string;
  selection_note: string;
  fallback_binding_ids: string[];
  records_ingested: number;
  latest_period: string | null;
  resolution_note: string;
}

export interface TerritorialRiskMapPoint {
  territorial_code: string;
  municipality_name: string;
  period: string;
  score: number;
  classification: RiskClassification;
  latitude: number;
  longitude: number;
}

export interface DataDrift {
  definition_id: string;
  latest_period: string | null;
  previous_period: string | null;
  latest_observation_count: number;
  previous_observation_count: number;
  observation_count_delta: number;
  latest_mean_value: number | null;
  previous_mean_value: number | null;
  mean_value_delta: number | null;
  drift_status: "stable" | "warning" | "alert" | "unknown";
  drift_note: string;
}

export interface Municipality {
  territorial_code: string;
  name: string;
  department_code: string;
  display_name: string;
}

export interface TerritorialReport {
  territorial_code: string;
  period: string;
  generated_at: string;
  risk: RiskScore;
  insights: Insight[];
  drift_status: string;
  drift_note: string;
  disclaimer: string;
}

export interface DepartmentMortalitySummary {
  department_code: string;
  department_name: string;
  observation_count: number;
  mean_mortality: number;
}

export interface BiasAnalysis {
  definition_id: string;
  period: string;
  national_mean: number;
  departments: DepartmentMortalitySummary[];
  analysis_note: string;
}

export interface GeoFeatureCollection {
  type: "FeatureCollection";
  features: Array<Record<string, unknown>>;
}

export interface HealthIndicator {
  id: string;
  definition_id: string;
  name: string;
  territorial_code: string;
  period: string;
  value: number;
  measurement_unit: string;
  source_id: string;
  ingested_at: string | null;
}

export interface RiskScore {
  territorial_code: string;
  period: string;
  score: number;
  classification: RiskClassification;
  model_version: string;
  indicator_definition_id: string;
  observed_value: number;
  baseline_value: number;
  assumptions: string[];
  drivers: string[];
  feature_contributions: FeatureContribution[];
  generated_at: string;
  persisted: boolean;
}

export interface AnomalyAlert {
  id: string;
  territorial_code: string;
  indicator_id: string;
  indicator_name: string;
  detected_on: string;
  severity: AnomalySeverity;
  description: string;
  baseline_value: number;
  observed_value: number;
}

export interface AnomalyAlertPage {
  items: AnomalyAlert[];
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
}

export interface TrendPoint {
  period: string;
  value: number;
  kind: TrendPointKind;
}

export interface TerritorialTrend {
  territorial_code: string;
  indicator_id: string;
  indicator_name: string;
  points: TrendPoint[];
  forecast_horizon_weeks: number;
  model_version: string;
  assumptions: string[];
}

export interface Insight {
  id: string;
  territorial_code: string;
  title: string;
  narrative: string;
  confidence: InsightConfidence;
  data_version: string;
  sources: string[];
  analysis_period?: string | null;
  system_context?: string | null;
}
