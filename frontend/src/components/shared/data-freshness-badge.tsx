"use client";

import { useApiResource } from "@/hooks/use-api-resource";
import { epidemiologicalApi } from "@/lib/api/client";

function formatTimestamp(value: string | null): string {
  if (!value) return "Sin ingestión registrada";
  return new Intl.DateTimeFormat("es-CO", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export function DataFreshnessBadge() {
  const { data, loading, error } = useApiResource(
    () => epidemiologicalApi.getDataFreshness(),
    [],
  );

  if (loading) {
    return (
      <p className="text-xs text-[var(--muted-foreground)]">Consultando frescura de datos…</p>
    );
  }

  if (error || !data) {
    return (
      <p className="text-xs text-[var(--muted-foreground)]">
        Frescura de datos no disponible
      </p>
    );
  }

  return (
    <div className="rounded-md border border-[var(--border)] bg-[var(--muted)]/40 px-3 py-2 text-xs text-[var(--muted-foreground)]">
      <p className="font-medium text-[var(--foreground)]">{data.source_name}</p>
      <p>Última ingestión: {formatTimestamp(data.last_successful_ingestion_at)}</p>
      <p>
        Periodo más reciente: {data.latest_period_available ?? "—"} ·{" "}
        {data.records_upserted ?? 0} registros
      </p>
    </div>
  );
}
