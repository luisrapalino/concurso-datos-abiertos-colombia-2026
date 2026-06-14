"use client";

import { useState } from "react";
import { Badge, severityBadgeVariant } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  EmptyState,
  ErrorState,
  LoadingState,
} from "@/components/shared/api-state";
import { epidemiologicalApi } from "@/lib/api/client";
import { useApiResource } from "@/hooks/use-api-resource";
import { useTerritorialFilters } from "@/stores/territorial-filters";

const severityLabels: Record<string, string> = {
  low: "Baja",
  medium: "Media",
  high: "Alta",
};

function AnomalyListContent({ territorialCode }: { territorialCode: string }) {
  const [page, setPage] = useState(1);
  const { data, error, loading, reload } = useApiResource(
    () =>
      epidemiologicalApi.listAnomalies({
        territorial_code: territorialCode,
        page,
        page_size: 10,
      }),
    [territorialCode, page],
  );

  if (loading) return <LoadingState message="Buscando anomalías..." />;
  if (error) return <ErrorState message={error} onRetry={reload} />;
  if (!data || data.items.length === 0) {
    return (
      <EmptyState message="No se detectaron anomalías para el territorio seleccionado." />
    );
  }

  return (
    <div className="space-y-4">
      <div className="overflow-x-auto rounded-lg border border-[var(--border)]">
        <table className="w-full min-w-[720px] text-left text-sm">
          <thead className="bg-[var(--muted)]/60 text-[var(--muted-foreground)]">
            <tr>
              <th className="px-4 py-3 font-medium">Indicador</th>
              <th className="px-4 py-3 font-medium">Severidad</th>
              <th className="px-4 py-3 font-medium">Observado</th>
              <th className="px-4 py-3 font-medium">Línea base</th>
              <th className="px-4 py-3 font-medium">Descripción</th>
            </tr>
          </thead>
          <tbody>
            {data.items.map((item) => (
              <tr
                key={item.id}
                className="border-t border-[var(--border)] align-top hover:bg-[var(--muted)]/30"
              >
                <td className="px-4 py-3">
                  <p className="font-medium">{item.indicator_name}</p>
                  <p className="text-xs text-[var(--muted-foreground)]">
                    {item.detected_on}
                  </p>
                </td>
                <td className="px-4 py-3">
                  <Badge variant={severityBadgeVariant(item.severity)}>
                    {severityLabels[item.severity] ?? item.severity}
                  </Badge>
                </td>
                <td className="px-4 py-3 tabular-nums">{item.observed_value.toFixed(2)}</td>
                <td className="px-4 py-3 tabular-nums">{item.baseline_value.toFixed(2)}</td>
                <td className="px-4 py-3 text-[var(--muted-foreground)]">
                  {item.description}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between text-sm text-[var(--muted-foreground)]">
        <span>
          Página {data.page} de {data.total_pages} · {data.total_items} alertas
        </span>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            disabled={data.page <= 1}
            onClick={() => setPage((current) => Math.max(1, current - 1))}
          >
            Anterior
          </Button>
          <Button
            variant="outline"
            size="sm"
            disabled={data.page >= data.total_pages}
            onClick={() => setPage((current) => current + 1)}
          >
            Siguiente
          </Button>
        </div>
      </div>
    </div>
  );
}

export function AnomalyList() {
  const { territorialCode } = useTerritorialFilters();

  return <AnomalyListContent key={territorialCode} territorialCode={territorialCode} />;
}
