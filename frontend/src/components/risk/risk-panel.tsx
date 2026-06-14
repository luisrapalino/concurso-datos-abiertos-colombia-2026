"use client";

import { Badge, riskBadgeVariant } from "@/components/ui/badge";
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

const classificationLabels: Record<string, string> = {
  low: "Bajo",
  medium: "Medio",
  high: "Alto",
  critical: "Crítico",
};

function RiskPanelContent({
  territorialCode,
  period,
}: {
  territorialCode: string;
  period: string;
}) {
  const { data: risk, error, loading, reload } = useApiResource(
    () => epidemiologicalApi.predictRisk({ territorial_code: territorialCode, period }),
    [territorialCode, period],
  );

  if (loading) return <LoadingState message="Calculando riesgo territorial..." />;
  if (error) return <ErrorState message={error} onRetry={reload} />;
  if (!risk) return <EmptyState message="Sin datos de riesgo disponibles." />;

  const drivers = risk.drivers ?? [];
  const assumptions = risk.assumptions ?? [];
  const featureContributions = risk.feature_contributions ?? [];

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Score de riesgo</CardTitle>
          <CardDescription>
            Modelo {risk.model_version} · {risk.indicator_definition_id}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-end gap-3">
            <span className="text-5xl font-bold tabular-nums text-[var(--primary)]">
              {risk.score.toFixed(1)}
            </span>
            <Badge variant={riskBadgeVariant(risk.classification)}>
              {classificationLabels[risk.classification] ?? risk.classification}
            </Badge>
          </div>
          <dl className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <dt className="text-[var(--muted-foreground)]">Valor observado</dt>
              <dd className="font-medium tabular-nums">{risk.observed_value.toFixed(2)}</dd>
            </div>
            <div>
              <dt className="text-[var(--muted-foreground)]">Línea base</dt>
              <dd className="font-medium tabular-nums">{risk.baseline_value.toFixed(2)}</dd>
            </div>
          </dl>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Factores explicativos</CardTitle>
          <CardDescription>Señales consideradas por el modelo explicable</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4 text-sm">
          <div>
            <p className="mb-2 font-medium">Drivers</p>
            <ul className="list-disc space-y-1 pl-5 text-[var(--muted-foreground)]">
              {drivers.map((driver) => (
                <li key={driver}>{driver}</li>
              ))}
            </ul>
          </div>
          <div>
            <p className="mb-2 font-medium">Contribuciones explicables</p>
            <ul className="space-y-2 text-[var(--muted-foreground)]">
              {featureContributions.length > 0 ? (
                featureContributions.map((item) => (
                  <li key={item.feature} className="rounded-md border border-[var(--border)] p-2">
                    <p className="font-medium text-[var(--foreground)]">{item.feature}</p>
                    <p className="text-xs">{item.description}</p>
                    <p className="mt-1 tabular-nums text-xs">
                      Valor {item.value.toFixed(2)} · Contribución {item.contribution.toFixed(1)}
                    </p>
                  </li>
                ))
              ) : (
                <li className="text-xs">
                  Contribuciones no disponibles en esta versión de la API. Reconstruye el
                  contenedor backend para obtener el desglose explicable.
                </li>
              )}
            </ul>
          </div>
          <div>
            <p className="mb-2 font-medium">Supuestos</p>
            <ul className="list-disc space-y-1 pl-5 text-[var(--muted-foreground)]">
              {assumptions.map((assumption) => (
                <li key={assumption}>{assumption}</li>
              ))}
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export function RiskPanel() {
  const { territorialCode, period } = useTerritorialFilters();

  return (
    <RiskPanelContent
      key={`${territorialCode}:${period}`}
      territorialCode={territorialCode}
      period={period}
    />
  );
}
