"use client";

import Link from "next/link";
import { useMemo } from "react";
import { ArrowRightIcon } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { PilotSignalChart } from "@/components/charts/pilot-signal-chart";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { SignalCardPresence } from "@/components/motion/signal-card-presence";
import { ResourcePresence } from "@/components/shared/resource-presence";
import { SignalReadout } from "@/components/shared/signal-readout";
import { epidemiologicalApi } from "@/lib/api/client";
import { riskClassificationLabels } from "@/lib/domain-labels";
import { riskBadgeVariant } from "@/lib/risk-badges";
import { useApiResource } from "@/hooks/use-api-resource";
import { useTerritorialFilters } from "@/stores/territorial-filters";
import { cn } from "@/lib/utils";

export function OutbreakAlertsPanel() {
  const {
    territorialCode,
    epidemiologicalPeriod,
    eventCode,
    setMunicipality,
    setEventCode,
  } = useTerritorialFilters();

  const { data: ranking, error, loading, reload } = useApiResource(
    () =>
      epidemiologicalApi.listOutbreakAlerts({
        period: epidemiologicalPeriod,
        event_code: eventCode,
        all_events: false,
        featured_only: true,
        limit: 15,
      }),
    [epidemiologicalPeriod, eventCode],
  );

  const { data: mapPoints } = useApiResource(
    () =>
      epidemiologicalApi.listOutbreakMap({
        period: epidemiologicalPeriod,
        event_code: eventCode,
        featured_only: true,
      }),
    [epidemiologicalPeriod, eventCode],
  );

  const { data: selectedRows } = useApiResource(
    () =>
      epidemiologicalApi.listOutbreakAlerts({
        period: epidemiologicalPeriod,
        event_code: eventCode,
        territorial_codes: territorialCode,
        featured_only: false,
        limit: 1,
      }),
    [epidemiologicalPeriod, eventCode, territorialCode],
  );

  const rows = useMemo(() => {
    if (!ranking?.length) return selectedRows ?? [];
    if (!selectedRows?.length) return ranking;
    const selected = selectedRows[0];
    if (ranking.some((alert) => alert.territorial_code === territorialCode)) {
      return ranking;
    }
    return [selected, ...ranking.filter((a) => a.territorial_code !== selected.territorial_code)].slice(0, 15);
  }, [ranking, selectedRows, territorialCode]);

  const selectedAlert = rows.find((a) => a.territorial_code === territorialCode);

  const resourceState = loading
    ? "loading"
    : error
      ? "error"
      : !rows.length
        ? "empty"
        : "ready";

  return (
    <ResourcePresence
      state={resourceState}
      loadingMessage="Cargando ranking territorial…"
      errorMessage={error ?? undefined}
      onRetry={reload}
      emptyMessage="Sin señales para esta enfermedad y semana"
      emptyHint="Prueba otra enfermedad o revisa si hay datos ingestados para el periodo."
    >
      <div className="space-y-4">
        <SignalCardPresence presenceKey={selectedAlert?.territorial_code ?? null}>
          {selectedAlert ? (
            <Card className="border-primary/15 bg-card/90">
              <CardContent className="pt-4">
                <SignalReadout
                  value={selectedAlert.outbreak_probability}
                  classification={selectedAlert.classification}
                  label={`${selectedAlert.municipality_name} · señal activa`}
                />
              </CardContent>
            </Card>
          ) : null}
        </SignalCardPresence>

      {mapPoints && mapPoints.length > 0 ? (
        <Card size="sm" className="bg-card/90">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Comparación ciudades piloto</CardTitle>
            <CardDescription>Señal relativa entre municipios con cobertura</CardDescription>
          </CardHeader>
          <CardContent>
            <PilotSignalChart points={mapPoints} selectedCode={territorialCode} />
          </CardContent>
        </Card>
      ) : null}

      <div className="overflow-x-auto rounded-lg border border-border/60 bg-card/90 shadow-sm">
        <table className="data-table">
          <thead>
            <tr>
              <th className="w-10">Pos.</th>
              <th>Municipio</th>
              <th>Señal</th>
              <th>Casos</th>
              <th>Factor principal</th>
              <th className="w-20" />
            </tr>
          </thead>
          <tbody>
            {rows.map((alert, index) => {
              const isSelected = alert.territorial_code === territorialCode;
              return (
                <tr
                  key={`${alert.territorial_code}-${alert.event_code}`}
                  className={cn(isSelected && "bg-primary/5")}
                >
                  <td className="tabular-nums text-muted-foreground">{index + 1}</td>
                  <td className="font-medium">
                    {alert.municipality_name}
                    {isSelected ? (
                      <span className="ml-2 text-xs font-normal text-primary">activo</span>
                    ) : null}
                  </td>
                  <td>
                    <div className="flex items-center gap-2">
                      <span className="font-mono font-semibold tabular-nums text-primary">
                        {alert.outbreak_probability.toFixed(1)}
                      </span>
                      <Badge variant={riskBadgeVariant(alert.classification)} className="text-xs">
                        {riskClassificationLabels[alert.classification] ?? alert.classification}
                      </Badge>
                    </div>
                  </td>
                  <td className="tabular-nums text-muted-foreground">
                    {alert.observed_cases.toFixed(0)} / {alert.baseline_cases.toFixed(0)}
                  </td>
                  <td className="max-w-[12rem] truncate text-muted-foreground">
                    {alert.top_driver ?? "—"}
                  </td>
                  <td>
                    <Link
                      href="/brotes"
                      className="inline-flex items-center gap-1 text-xs font-medium text-primary underline-offset-4 hover:underline"
                      onClick={() => {
                        setMunicipality(alert.territorial_code, alert.municipality_name);
                        setEventCode(alert.event_code);
                      }}
                    >
                      Ver ficha
                      <ArrowRightIcon className="size-3" />
                    </Link>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      </div>
    </ResourcePresence>
  );
}
