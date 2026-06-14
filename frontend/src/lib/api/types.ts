export type RiskClassification = "low" | "medium" | "high" | "critical";
export type AnomalySeverity = "low" | "medium" | "high";
export type TrendPointKind = "historical" | "forecast";
export type InsightConfidence = "low" | "medium" | "high";

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

export interface TerritorialRiskMapPoint {
  territorial_code: string;
  period: string;
  score: number;
  classification: RiskClassification;
  latitude: number;
  longitude: number;
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
