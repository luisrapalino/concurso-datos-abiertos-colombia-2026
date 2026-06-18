"use client";

import { Badge } from "@/components/ui/badge";
import { riskBadgeVariant } from "@/lib/risk-badges";
import { Button } from "@/components/ui/button";
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

import { driftStatusLabels, riskClassificationLabels } from "@/lib/domain-labels";

function ReportContent({
  territorialCode,
  period,
}: {
  territorialCode: string;
  period: string;
}) {
  const { data, error, loading, reload } = useApiResource(
    () => epidemiologicalApi.getTerritorialReport({ territorial_code: territorialCode, period }),
    [territorialCode, period],
  );

  if (loading) return <LoadingState message="Generando informe territorial..." />;
  if (error) return <ErrorState message={error} onRetry={reload} />;
  if (!data) return <EmptyState message="Sin datos para el informe." />;

  return (
    <div id="territorial-report" className="space-y-4 print:space-y-3">
      <div className="flex flex-wrap items-start justify-between gap-3 print:hidden">
        <p className="text-sm text-[var(--muted-foreground)]">
          Generado {new Intl.DateTimeFormat("es-CO", { dateStyle: "long", timeStyle: "short" }).format(new Date(data.generated_at))}
        </p>
        <Button type="button" variant="outline" onClick={() => window.print()}>
          Exportar / imprimir PDF
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Resumen ejecutivo</CardTitle>
          <CardDescription>
            Territorio {data.territorial_code} · periodo {data.period}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3 text-sm">
          <div className="flex flex-wrap items-center gap-2">
            <span>
              Nivel de riesgo:{" "}
              <span className="font-semibold tabular-nums">{data.risk.score.toFixed(1)}</span>
            </span>
            <Badge variant={riskBadgeVariant(data.risk.classification)}>
              {riskClassificationLabels[data.risk.classification] ?? data.risk.classification}
            </Badge>
          </div>
          <p>Modelo: {data.risk.model_version}</p>
          <p>
            Cambios en los datos:{" "}
            <span className="font-medium">
              {driftStatusLabels[data.drift_status] ?? data.drift_status}
            </span>
            {" — "}
            {data.drift_note}
          </p>
          <p className="text-[var(--muted-foreground)]">{data.disclaimer}</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Motivos principales</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="list-disc space-y-1 pl-5 text-sm">
            {(data.risk.drivers ?? []).map((driver) => (
              <li key={driver}>{driver}</li>
            ))}
          </ul>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Lectura automática</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {data.insights.map((insight) => (
            <article key={insight.id} className="rounded-md border border-[var(--border)] p-3">
              <h3 className="font-semibold">{insight.title}</h3>
              <p className="mt-1 text-sm text-[var(--muted-foreground)]">{insight.narrative}</p>
            </article>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}

export function TerritorialReportPanel() {
  const { territorialCode, period } = useTerritorialFilters();
  return <ReportContent territorialCode={territorialCode} period={period} />;
}
