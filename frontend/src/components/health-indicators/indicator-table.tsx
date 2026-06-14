"use client";

import {
  EmptyState,
  ErrorState,
  LoadingState,
} from "@/components/shared/api-state";
import { epidemiologicalApi } from "@/lib/api/client";
import type { HealthIndicator } from "@/lib/api/types";
import { useApiResource } from "@/hooks/use-api-resource";
import { useTerritorialFilters } from "@/stores/territorial-filters";

function IndicatorTableContent({
  territorialCode,
  period,
}: {
  territorialCode: string;
  period: string;
}) {
  const { data, error, loading, reload } = useApiResource(
    () =>
      epidemiologicalApi.listHealthIndicators({
        territorial_code: territorialCode,
        period,
        limit: 50,
      }),
    [territorialCode, period],
  );

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} onRetry={reload} />;

  const items = data ?? [];
  if (items.length === 0) {
    return (
      <EmptyState message="No hay observaciones para el territorio y periodo seleccionados." />
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-[var(--border)]">
      <table className="w-full min-w-[640px] text-left text-sm">
        <thead className="bg-[var(--muted)]/60 text-[var(--muted-foreground)]">
          <tr>
            <th className="px-4 py-3 font-medium">Indicador</th>
            <th className="px-4 py-3 font-medium">Territorio</th>
            <th className="px-4 py-3 font-medium">Periodo</th>
            <th className="px-4 py-3 font-medium">Valor</th>
            <th className="px-4 py-3 font-medium">Unidad</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item: HealthIndicator) => (
            <tr
              key={item.id}
              className="border-t border-[var(--border)] hover:bg-[var(--muted)]/30"
            >
              <td className="px-4 py-3 font-medium">{item.name}</td>
              <td className="px-4 py-3">{item.territorial_code}</td>
              <td className="px-4 py-3">{item.period}</td>
              <td className="px-4 py-3 tabular-nums">{item.value.toFixed(2)}</td>
              <td className="px-4 py-3">{item.measurement_unit}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function IndicatorTable() {
  const { territorialCode, period } = useTerritorialFilters();

  return (
    <IndicatorTableContent
      key={`${territorialCode}:${period}`}
      territorialCode={territorialCode}
      period={period}
    />
  );
}
