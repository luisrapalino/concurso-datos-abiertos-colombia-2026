"use client";

import type { ComponentType } from "react";
import { ExternalLinkIcon, LayersIcon, MapPinIcon, DatabaseIcon } from "lucide-react";
import { ResourcePresence } from "@/components/shared/resource-presence";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useApiResource } from "@/hooks/use-api-resource";
import { epidemiologicalApi } from "@/lib/api/client";
import type { DatasetCatalogEntry, MunicipalVariableDataset } from "@/lib/api/types";

const numberFormatter = new Intl.NumberFormat("es-CO");

function formatPeriod(period: string | null): string {
  if (!period) return "—";
  if (/^\d{4}-W\d{2}$/.test(period)) {
    return `Sem. ${period.replace("-W", " ")}`;
  }
  return period;
}

function formatIngestionDate(value: string | null): string {
  if (!value) return "Sin ingestión registrada";
  return new Intl.DateTimeFormat("es-CO", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function SourceLinks({
  portalUrl,
  apiUrl,
}: {
  portalUrl: string;
  apiUrl: string;
}) {
  return (
    <div className="flex flex-wrap gap-2">
      <a
        href={portalUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="inline-flex items-center gap-1 text-xs text-primary underline-offset-4 hover:underline"
      >
        Portal datos.gov.co
        <ExternalLinkIcon className="size-3" />
      </a>
      <a
        href={apiUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="inline-flex items-center gap-1 text-xs text-muted-foreground underline-offset-4 hover:text-foreground hover:underline"
      >
        API SODA
        <ExternalLinkIcon className="size-3" />
      </a>
    </div>
  );
}

function groupByMunicipality(rows: MunicipalVariableDataset[]) {
  const groups = new Map<string, MunicipalVariableDataset[]>();
  for (const row of rows) {
    const key = row.territorial_code;
    const current = groups.get(key) ?? [];
    current.push(row);
    groups.set(key, current);
  }
  return groups;
}

function MetricTile({
  icon: Icon,
  label,
  value,
  detail,
}: {
  icon: ComponentType<{ className?: string }>;
  label: string;
  value: string;
  detail?: string;
}) {
  return (
    <div className="rounded-lg border border-border/60 bg-card/90 p-4 shadow-sm">
      <div className="flex items-start gap-3">
        <div className="flex size-8 shrink-0 items-center justify-center rounded-md bg-primary/10 text-primary">
          <Icon className="size-4" />
        </div>
        <div className="min-w-0">
          <p className="text-xs text-muted-foreground">{label}</p>
          <p className="font-mono text-xl font-semibold tabular-nums text-foreground">{value}</p>
          {detail ? (
            <p className="mt-0.5 text-xs text-muted-foreground">{detail}</p>
          ) : null}
        </div>
      </div>
    </div>
  );
}

export function DatasetsPanel() {
  const summary = useApiResource(() => epidemiologicalApi.listDatasets(), []);
  const municipal = useApiResource(
    () => epidemiologicalApi.listMunicipalVariableDatasets(),
    [],
  );

  const loading = summary.loading || municipal.loading;
  const error = summary.error ?? municipal.error;
  const reload = () => {
    summary.reload();
    municipal.reload();
  };

  const totalRecords =
    summary.data?.reduce((sum, item) => sum + item.records_ingested, 0) ?? 0;
  const municipalGroups = municipal.data ? groupByMunicipality(municipal.data) : null;
  const indicatorCount = summary.data?.length ?? 0;
  const municipalityCount = municipalGroups?.size ?? 0;

  const resourceState = loading
    ? "loading"
    : error
      ? "error"
      : !summary.data?.length
        ? "empty"
        : "ready";

  return (
    <ResourcePresence
      state={resourceState}
      loadingMessage="Consultando catálogo de datos…"
      errorMessage={error ?? undefined}
      onRetry={reload}
      emptyMessage="No hay indicadores registrados"
      emptyHint="Ejecuta la ingestión de datos abiertos para poblar el catálogo."
    >
      {summary.data?.length ? (
    <div className="space-y-5">
      <div className="grid gap-3 sm:grid-cols-3">
        <MetricTile
          icon={DatabaseIcon}
          label="Registros ingestados"
          value={numberFormatter.format(totalRecords)}
          detail="Total acumulado en la plataforma"
        />
        <MetricTile
          icon={LayersIcon}
          label="Indicadores"
          value={String(indicatorCount)}
          detail="Variables con cobertura registrada"
        />
        <MetricTile
          icon={MapPinIcon}
          label="Municipios piloto"
          value={String(municipalityCount)}
          detail="Ciudades con resolución de datasets"
        />
      </div>

      {municipalGroups ? (
        <div className="space-y-3">
          <h2 className="text-sm font-medium text-foreground">Cobertura por municipio</h2>
          <div className="grid gap-3">
            {[...municipalGroups.entries()].map(([code, rows]) => (
              <Card key={code} className="bg-card/90">
                <CardHeader className="border-b border-border/60 pb-3">
                  <CardTitle className="text-sm font-medium">
                    {rows[0]?.municipality_name ?? code}
                  </CardTitle>
                  <CardDescription>
                    Código DANE {code} · {rows.length} variables resueltas
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3 pt-4">
                  {rows.map((row) => (
                    <div
                      key={`${row.territorial_code}:${row.definition_id}`}
                      className="rounded-lg border border-border/60 bg-background/50 p-3 text-sm"
                    >
                      <div className="flex flex-wrap items-start justify-between gap-2">
                        <div className="space-y-1">
                          <p className="font-medium">{row.variable_name}</p>
                          <p className="font-mono text-xs text-muted-foreground">
                            {row.active_binding_id} · {row.granularity}
                          </p>
                        </div>
                        <Badge variant={row.records_ingested > 0 ? "default" : "secondary"}>
                          {numberFormatter.format(row.records_ingested)} registros
                        </Badge>
                      </div>
                      <p className="mt-2 text-xs leading-relaxed text-muted-foreground">
                        {row.resolution_note}
                      </p>
                      <dl className="mt-3 grid gap-2 border-t border-border/40 pt-3 sm:grid-cols-2">
                        <div>
                          <dt className="text-xs text-muted-foreground">Último periodo</dt>
                          <dd className="font-medium">{formatPeriod(row.latest_period)}</dd>
                        </div>
                        <div>
                          <dt className="text-xs text-muted-foreground">Respaldo</dt>
                          <dd className="font-mono text-xs">
                            {row.fallback_binding_ids.length
                              ? row.fallback_binding_ids.join(", ")
                              : "—"}
                          </dd>
                        </div>
                      </dl>
                      <div className="mt-3">
                        <SourceLinks portalUrl={row.portal_url} apiUrl={row.api_url} />
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      ) : null}

      <Card className="bg-card/90">
        <CardHeader className="border-b border-border/60 pb-3">
          <CardTitle className="text-sm font-medium">Totales por indicador</CardTitle>
          <CardDescription>Volumen y frescura de cada fuente integrada</CardDescription>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="overflow-x-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Indicador</th>
                  <th>Municipios</th>
                  <th>Último periodo</th>
                  <th>Ingestión</th>
                  <th className="text-right">Registros</th>
                </tr>
              </thead>
              <tbody>
                {summary.data.map((dataset: DatasetCatalogEntry) => (
                  <tr key={dataset.definition_id}>
                    <td className="font-medium">{dataset.name}</td>
                    <td className="tabular-nums text-muted-foreground">
                      {dataset.municipalities_count}
                    </td>
                    <td className="text-muted-foreground">
                      {formatPeriod(dataset.latest_period)}
                    </td>
                    <td className="text-xs text-muted-foreground">
                      {formatIngestionDate(dataset.last_ingestion_at)}
                    </td>
                    <td className="text-right">
                      <Badge variant="outline" className="font-mono">
                        {numberFormatter.format(dataset.records_ingested)}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
      ) : null}
    </ResourcePresence>
  );
}
