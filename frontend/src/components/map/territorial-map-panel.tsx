"use client";

import Link from "next/link";
import { ArrowRightIcon } from "lucide-react";
import { ColombiaTerritorialChart } from "@/components/map/colombia-territorial-chart";
import { SignalCardPresence } from "@/components/motion/signal-card-presence";
import { ResourcePresence } from "@/components/shared/resource-presence";
import { SignalReadout } from "@/components/shared/signal-readout";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { MapClassification } from "@/components/map/colombia-map-theme";
import { useMapTheme } from "@/hooks/use-map-theme";
import { epidemiologicalApi } from "@/lib/api/client";
import type { GeoFeatureCollection, OutbreakMapPoint } from "@/lib/api/types";
import { formatMunicipalityName, riskClassificationLabels } from "@/lib/domain-labels";
import { useApiResource } from "@/hooks/use-api-resource";
import { useTerritorialFilters } from "@/stores/territorial-filters";

function MapLegend({ colors }: { colors: Record<MapClassification, string> }) {
  return (
    <div className="flex flex-wrap gap-4 text-xs text-muted-foreground">
      {(Object.keys(colors) as MapClassification[]).map((level) => (
        <span key={level} className="inline-flex items-center gap-1.5">
          <span
            className="size-2.5 rounded-full ring-1 ring-border/60"
            style={{ backgroundColor: colors[level] }}
            aria-hidden
          />
          {riskClassificationLabels[level] ?? level}
        </span>
      ))}
    </div>
  );
}

function TerritorialMapContent({
  epidemiologicalPeriod,
  eventCode,
  selectedCode,
  onSelectMunicipality,
}: {
  epidemiologicalPeriod: string;
  eventCode: string;
  selectedCode: string;
  onSelectMunicipality: (code: string, name: string) => void;
}) {
  const outbreakQuery = useApiResource(
    () =>
      epidemiologicalApi.listOutbreakMap({
        period: epidemiologicalPeriod,
        event_code: eventCode,
        featured_only: true,
      }),
    [epidemiologicalPeriod, eventCode],
  );
  const boundariesQuery = useApiResource(
    () => epidemiologicalApi.getTerritorialBoundaries("department"),
    [],
  );

  const { classificationColors } = useMapTheme();

  const points = outbreakQuery.data;
  const loading = outbreakQuery.loading || boundariesQuery.loading;
  const error = outbreakQuery.error ?? boundariesQuery.error;

  const boundaryData = boundariesQuery.data as GeoFeatureCollection | null;

  const selectedPoint = points?.find((p) => p.territorial_code === selectedCode);

  const resourceState = loading
    ? "loading"
    : error
      ? "error"
      : !points?.length
        ? "empty"
        : "ready";

  return (
    <ResourcePresence
      state={resourceState}
      loadingMessage="Cargando mapa territorial…"
      errorMessage={error ?? undefined}
      onRetry={outbreakQuery.reload}
      emptyMessage="Sin datos geográficos para esta semana"
      emptyHint="Prueba otra enfermedad o verifica la ingestión de SIVIGILA."
    >
      {points?.length ? (
    <div className="space-y-4">
      <SignalCardPresence presenceKey={selectedPoint?.territorial_code ?? null}>
        {selectedPoint ? (
        <Card className="border-primary/15 bg-card/90">
          <CardContent className="flex flex-wrap items-center justify-between gap-4 pt-4">
            <SignalReadout
              size="sm"
              value={selectedPoint.outbreak_probability}
              classification={selectedPoint.classification}
              label={formatMunicipalityName(selectedPoint.municipality_name)}
            />
            <Link
              href="/brotes"
              className="inline-flex items-center gap-1 text-xs font-medium text-primary underline-offset-4 hover:underline"
            >
              Abrir ficha
              <ArrowRightIcon className="size-3" />
            </Link>
          </CardContent>
        </Card>
        ) : null}
      </SignalCardPresence>

      <Card className="overflow-hidden bg-card/90 p-0">
        <CardHeader className="border-b border-border/60 px-4 py-3">
          <CardTitle className="text-sm font-medium">Distribución por clasificación</CardTitle>
          <CardDescription>
            Haz clic en un municipio para seleccionarlo en los filtros
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3 px-4 pt-3 pb-4">
          <MapLegend colors={classificationColors} />
          <ColombiaTerritorialChart
            boundaryData={boundaryData}
            points={points as OutbreakMapPoint[]}
            selectedCode={selectedCode}
            onSelectMunicipality={onSelectMunicipality}
          />
        </CardContent>
      </Card>
    </div>
      ) : null}
    </ResourcePresence>
  );
}

export function TerritorialMapPanel() {
  const {
    period,
    epidemiologicalPeriod,
    eventCode,
    territorialCode,
    setMunicipality,
  } = useTerritorialFilters();

  return (
    <TerritorialMapContent
      key={`${period}:${epidemiologicalPeriod}:${eventCode}`}
      epidemiologicalPeriod={epidemiologicalPeriod}
      eventCode={eventCode}
      selectedCode={territorialCode}
      onSelectMunicipality={setMunicipality}
    />
  );
}
