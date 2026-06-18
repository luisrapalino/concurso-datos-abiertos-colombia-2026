"use client";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { FeatureContributionsChart } from "@/components/charts/feature-contributions-chart";
import { TrendChart } from "@/components/charts/trend-chart";
import {
  EmptyState,
  LoadingState,
} from "@/components/shared/api-state";
import { ResourcePresence } from "@/components/shared/resource-presence";
import { SignalReadout } from "@/components/shared/signal-readout";
import { epidemiologicalApi } from "@/lib/api/client";
import { resolveEventDefinitionId } from "@/lib/sivigila-events";
import { useApiResource } from "@/hooks/use-api-resource";
import { useTerritorialFilters } from "@/stores/territorial-filters";

function OutbreakPanelContent({
  territorialCode,
  period,
  eventCode,
}: {
  territorialCode: string;
  period: string;
  eventCode: string;
}) {
  const definitionId = resolveEventDefinitionId(eventCode);

  const { data: prediction, error, loading, reload } = useApiResource(
    () =>
      epidemiologicalApi.predictOutbreak({
        territorial_code: territorialCode,
        period,
        event_code: eventCode,
      }),
    [territorialCode, period, eventCode],
  );

  const trendQuery = useApiResource(
    () => {
      if (!definitionId) {
        return Promise.reject(new Error("Enfermedad no reconocida"));
      }
      return epidemiologicalApi.getTerritorialTrends({
        territorial_code: territorialCode,
        indicator_id: definitionId,
        horizon_weeks: 4,
      });
    },
    [territorialCode, definitionId],
  );

  const resourceState = loading
    ? "loading"
    : error
      ? "error"
      : !prediction
        ? "empty"
        : "ready";

  return (
    <ResourcePresence
      state={resourceState}
      loadingMessage="Calculando señal territorial…"
      errorMessage={error ?? undefined}
      onRetry={reload}
      emptyMessage="Sin datos para este municipio y semana"
      emptyHint="Selecciona otro municipio o verifica la cobertura de datos."
    >
      {prediction ? (
    <div className="space-y-4">
      <div className="grid gap-4 lg:grid-cols-2">
        <Card size="sm" className="border-primary/15 bg-card/90">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">{prediction.event_name}</CardTitle>
            <CardDescription>Semana epidemiológica activa</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <SignalReadout
              value={prediction.outbreak_probability}
              classification={prediction.classification}
            />
            <dl className="grid grid-cols-2 gap-3 border-t border-border/60 pt-3 text-sm">
              <div>
                <dt className="text-xs text-muted-foreground">Casos observados</dt>
                <dd className="font-mono font-medium tabular-nums">
                  {prediction.observed_cases.toFixed(0)}
                </dd>
              </div>
              <div>
                <dt className="text-xs text-muted-foreground">Mediana nacional</dt>
                <dd className="font-mono font-medium tabular-nums">
                  {prediction.baseline_cases.toFixed(1)}
                </dd>
              </div>
            </dl>
          </CardContent>
        </Card>

        <Card size="sm" className="bg-card/90">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Contribución por factor</CardTitle>
            <CardDescription>Variables que explican la señal</CardDescription>
          </CardHeader>
          <CardContent>
            <FeatureContributionsChart contributions={prediction.feature_contributions} />
          </CardContent>
        </Card>
      </div>

      <Card size="sm" className="bg-card/90">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Casos semanales</CardTitle>
          <CardDescription>Serie histórica y proyección a 4 semanas</CardDescription>
        </CardHeader>
        <CardContent>
          {trendQuery.loading ? (
            <LoadingState message="Cargando serie…" />
          ) : trendQuery.error ? (
            <EmptyState
              message="Sin serie histórica para esta enfermedad"
              hint="Puede que aún no haya datos ingestados para el municipio."
            />
          ) : trendQuery.data ? (
            <TrendChart trend={trendQuery.data} />
          ) : null}
        </CardContent>
      </Card>
    </div>
      ) : null}
    </ResourcePresence>
  );
}

export function OutbreakPanel() {
  const { territorialCode, epidemiologicalPeriod, eventCode } = useTerritorialFilters();
  return (
    <OutbreakPanelContent
      key={`${territorialCode}:${epidemiologicalPeriod}:${eventCode}`}
      territorialCode={territorialCode}
      period={epidemiologicalPeriod}
      eventCode={eventCode}
    />
  );
}
