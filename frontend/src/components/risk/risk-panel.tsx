"use client";

import { Badge } from "@/components/ui/badge";
import { riskBadgeVariant } from "@/lib/risk-badges";
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
import { riskClassificationLabels } from "@/lib/domain-labels";
import { useApiResource } from "@/hooks/use-api-resource";
import { useTerritorialFilters } from "@/stores/territorial-filters";

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

  if (loading) return <LoadingState message="Calculando nivel de riesgo..." />;
  if (error) return <ErrorState message={error} onRetry={reload} />;
  if (!risk) return <EmptyState message="No hay datos de riesgo para este municipio y periodo." />;

  const drivers = risk.drivers ?? [];
  const assumptions = risk.assumptions ?? [];
  const featureContributions = risk.feature_contributions ?? [];

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Nivel de riesgo</CardTitle>
          <CardDescription>
            Escala de 0 a 100 · comparado con el promedio nacional del mismo periodo
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-end gap-3">
            <span className="text-5xl font-bold tabular-nums text-[var(--primary)]">
              {risk.score.toFixed(1)}
            </span>
            <Badge variant={riskBadgeVariant(risk.classification)}>
              {riskClassificationLabels[risk.classification] ?? risk.classification}
            </Badge>
          </div>
          <dl className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <dt className="text-[var(--muted-foreground)]">Mortalidad en el municipio</dt>
              <dd className="font-medium tabular-nums">{risk.observed_value.toFixed(2)}</dd>
            </div>
            <div>
              <dt className="text-[var(--muted-foreground)]">Promedio nacional</dt>
              <dd className="font-medium tabular-nums">{risk.baseline_value.toFixed(2)}</dd>
            </div>
          </dl>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>¿Por qué este resultado?</CardTitle>
          <CardDescription>Factores que el sistema tuvo en cuenta</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4 text-sm">
          <div>
            <p className="mb-2 font-medium">Motivos principales</p>
            <ul className="list-disc space-y-1 pl-5 text-[var(--muted-foreground)]">
              {drivers.map((driver) => (
                <li key={driver}>{driver}</li>
              ))}
            </ul>
          </div>
          <div>
            <p className="mb-2 font-medium">Detalle de cada factor</p>
            <ul className="space-y-2 text-[var(--muted-foreground)]">
              {featureContributions.length > 0 ? (
                featureContributions.map((item) => (
                  <li key={item.feature} className="rounded-md border border-[var(--border)] p-2">
                    <p className="font-medium text-[var(--foreground)]">{item.feature}</p>
                    <p className="text-xs">{item.description}</p>
                    <p className="mt-1 tabular-nums text-xs">
                      Valor {item.value.toFixed(2)} · Peso en el resultado{" "}
                      {item.contribution.toFixed(1)}
                    </p>
                  </li>
                ))
              ) : (
                <li className="text-xs">Detalle no disponible en esta versión.</li>
              )}
            </ul>
          </div>
          <div>
            <p className="mb-2 font-medium">Ten en cuenta</p>
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
