"use client";

import { DownloadIcon, PrinterIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ResourcePresence } from "@/components/shared/resource-presence";
import { SignalReadout } from "@/components/shared/signal-readout";
import { epidemiologicalApi } from "@/lib/api/client";
import { FeatureContributionsChart } from "@/components/charts/feature-contributions-chart";
import { TrendChart } from "@/components/charts/trend-chart";
import {
  formatMunicipalityName,
  formatPeriodLabel,
  riskClassificationLabels,
} from "@/lib/domain-labels";
import { resolveEventDefinitionId } from "@/lib/sivigila-events";
import { useApiResource } from "@/hooks/use-api-resource";
import { useTerritorialFilters } from "@/stores/territorial-filters";

function formatGeneratedAt(date: Date): string {
  return new Intl.DateTimeFormat("es-CO", {
    dateStyle: "long",
    timeStyle: "short",
  }).format(date);
}

function ReportBody({
  territorialCode,
  municipalityName,
  period,
  eventCode,
}: {
  territorialCode: string;
  municipalityName: string | null;
  period: string;
  eventCode: string;
}) {
  const definitionId = resolveEventDefinitionId(eventCode);
  const generatedAt = formatGeneratedAt(new Date());

  const { data, error, loading, reload } = useApiResource(
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
      : !data
        ? "empty"
        : "ready";

  const territoryLabel = formatMunicipalityName(
    municipalityName ?? territorialCode,
  );

  return (
    <ResourcePresence
      state={resourceState}
      loadingMessage="Generando informe territorial…"
      errorMessage={error ?? undefined}
      onRetry={reload}
      emptyMessage="Sin datos para este municipio y semana"
      emptyHint="Ajusta los filtros o verifica la cobertura de ingestión."
    >
      {data ? (
    <div id="outbreak-report" className="print-report space-y-4 print:space-y-3">
      <div className="flex flex-wrap items-center justify-end gap-2 print:hidden">
        <Button type="button" variant="outline" size="sm" onClick={() => window.print()}>
          <PrinterIcon className="size-3.5" />
          Imprimir informe
        </Button>
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={() => window.print()}
          title="Usa «Guardar como PDF» en el diálogo de impresión"
        >
          <DownloadIcon className="size-3.5" />
          Exportar PDF
        </Button>
      </div>

      <header className="print-masthead hidden border-b-2 border-primary pb-4 print:block">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-[10px] font-medium tracking-[0.2em] text-primary uppercase">
              Radar de Brotes
            </p>
            <h1 className="mt-1 text-xl font-semibold text-foreground">
              Informe territorial
            </h1>
            <p className="mt-1 text-sm text-muted-foreground">
              {data.event_name} · {territoryLabel}
            </p>
          </div>
          <dl className="text-right text-[10px] text-muted-foreground">
            <div>
              <dt className="inline">Generado: </dt>
              <dd className="inline font-medium text-foreground">{generatedAt}</dd>
            </div>
            <div className="mt-1">
              <dt className="inline">Periodo: </dt>
              <dd className="inline">{formatPeriodLabel(period)}</dd>
            </div>
            <div>
              <dt className="inline">DANE: </dt>
              <dd className="inline font-mono">{territorialCode}</dd>
            </div>
          </dl>
        </div>
      </header>

      <Card
        size="sm"
        className="border-primary/15 bg-card/90 print:border print:bg-white print:shadow-none"
      >
        <CardHeader className="border-b border-border/60 pb-3 print:pb-2">
          <p className="text-xs font-medium tracking-widest text-primary uppercase print:text-[10px]">
            Informe de señal
          </p>
          <CardTitle className="text-lg print:text-base">
            {data.event_name} · {territoryLabel}
          </CardTitle>
          <CardDescription className="print:text-xs">
            {formatPeriodLabel(period)} · código DANE {territorialCode}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4 pt-4">
          <SignalReadout
            value={data.outbreak_probability}
            classification={data.classification}
          />
          <dl className="grid gap-3 border-t border-border/60 pt-3 sm:grid-cols-3">
            <div>
              <dt className="text-xs text-muted-foreground">Casos observados</dt>
              <dd className="font-mono text-base font-medium tabular-nums">
                {data.observed_cases.toFixed(0)}
              </dd>
            </div>
            <div>
              <dt className="text-xs text-muted-foreground">Mediana nacional</dt>
              <dd className="font-mono text-base font-medium tabular-nums">
                {data.baseline_cases.toFixed(1)}
              </dd>
            </div>
            <div>
              <dt className="text-xs text-muted-foreground">Clasificación</dt>
              <dd className="text-sm font-medium">
                {riskClassificationLabels[data.classification] ?? data.classification}
              </dd>
            </div>
            <div className="sm:col-span-3">
              <dt className="text-xs text-muted-foreground">Versión del modelo</dt>
              <dd className="font-mono text-sm font-medium">{data.model_version}</dd>
            </div>
          </dl>
        </CardContent>
      </Card>

      <Card
        size="sm"
        className="bg-card/90 print:break-inside-avoid print:border print:bg-white print:shadow-none"
      >
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Contribución por factor</CardTitle>
          <CardDescription className="print:hidden">
            Variables que explican la señal calculada
          </CardDescription>
        </CardHeader>
        <CardContent>
          <FeatureContributionsChart contributions={data.feature_contributions} height={200} />
        </CardContent>
      </Card>

      {trendQuery.data ? (
        <Card
          size="sm"
          className="bg-card/90 print:break-inside-avoid print:border print:bg-white print:shadow-none"
        >
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Casos semanales</CardTitle>
            <CardDescription className="print:hidden">
              Serie histórica y proyección a 4 semanas
            </CardDescription>
          </CardHeader>
          <CardContent>
            <TrendChart trend={trendQuery.data} height={260} />
          </CardContent>
        </Card>
      ) : null}

      <footer className="rounded-lg border border-border/60 bg-muted/30 px-4 py-3 text-xs text-muted-foreground print:mt-4 print:rounded-none print:border-t-2 print:border-primary/30 print:bg-transparent print:px-0 print:pt-3 print:text-[9pt]">
        <p>{data.assumptions[0]}</p>
        <p className="mt-1 font-medium text-foreground">
          Requiere validación epidemiológica antes de tomar decisiones operativas.
        </p>
        <p className="mt-2 hidden text-muted-foreground print:block">
          Documento generado por Radar de Brotes · datos abiertos Colombia
        </p>
      </footer>
    </div>
      ) : null}
    </ResourcePresence>
  );
}

export function OutbreakReportPanel() {
  const { territorialCode, municipalityName, epidemiologicalPeriod, eventCode } =
    useTerritorialFilters();
  return (
    <ReportBody
      key={`${territorialCode}:${epidemiologicalPeriod}:${eventCode}`}
      territorialCode={territorialCode}
      municipalityName={municipalityName}
      period={epidemiologicalPeriod}
      eventCode={eventCode}
    />
  );
}
