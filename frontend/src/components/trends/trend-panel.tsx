"use client";

import { TrendChart } from "@/components/charts/trend-chart";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  EmptyState,
  ErrorState,
  LoadingState,
} from "@/components/shared/api-state";
import { epidemiologicalApi } from "@/lib/api/client";
import { useApiResource } from "@/hooks/use-api-resource";
import { useTerritorialFilters } from "@/stores/territorial-filters";

function TrendPanelContent({ territorialCode }: { territorialCode: string }) {
  const { data: trend, error, loading, reload } = useApiResource(
    () =>
      epidemiologicalApi.getTerritorialTrends({
        territorial_code: territorialCode,
        horizon_weeks: 4,
      }),
    [territorialCode],
  );

  if (loading) return <LoadingState message="Construyendo serie temporal..." />;
  if (error) return <ErrorState message={error} onRetry={reload} />;
  if (!trend || trend.points.length === 0) {
    return <EmptyState message="No hay puntos históricos para proyectar tendencias." />;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{trend.indicator_name}</CardTitle>
        <CardDescription>
          Modelo {trend.model_version} · Horizonte {trend.forecast_horizon_weeks} semanas
        </CardDescription>
      </CardHeader>
      <CardContent>
        <TrendChart trend={trend} />
      </CardContent>
    </Card>
  );
}

export function TrendPanel() {
  const { territorialCode } = useTerritorialFilters();

  return <TrendPanelContent key={territorialCode} territorialCode={territorialCode} />;
}
