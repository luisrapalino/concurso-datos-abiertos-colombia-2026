"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { useMemo } from "react";
import { ArrowRightIcon } from "lucide-react";
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
import {
  COLOMBIA_CENTER,
  type MapClassification,
} from "@/components/map/colombia-map-theme";
import { useMapTheme } from "@/hooks/use-map-theme";
import { epidemiologicalApi } from "@/lib/api/client";
import type { GeoFeatureCollection, OutbreakMapPoint } from "@/lib/api/types";
import { formatMunicipalityName, riskClassificationLabels } from "@/lib/domain-labels";
import { useApiResource } from "@/hooks/use-api-resource";
import { useTerritorialFilters } from "@/stores/territorial-filters";

const MapContainer = dynamic(
  async () => (await import("react-leaflet")).MapContainer,
  { ssr: false },
);
const CircleMarker = dynamic(
  async () => (await import("react-leaflet")).CircleMarker,
  { ssr: false },
);
const Tooltip = dynamic(async () => (await import("react-leaflet")).Tooltip, { ssr: false });
const GeoJSON = dynamic(async () => (await import("react-leaflet")).GeoJSON, {
  ssr: false,
});
const MapFitColombiaLayer = dynamic(
  () => import("@/components/map/map-fit-colombia").then((mod) => mod.MapFitColombia),
  { ssr: false },
);

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

  const { theme: mapTheme, classificationColors } = useMapTheme();

  const points = outbreakQuery.data;
  const loading = outbreakQuery.loading || boundariesQuery.loading;
  const error = outbreakQuery.error ?? boundariesQuery.error;

  const boundaryData = useMemo(
    () => boundariesQuery.data as GeoFeatureCollection | null,
    [boundariesQuery.data],
  );

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
          <div
            className="colombia-map h-[440px] overflow-hidden rounded-lg border border-border/60 shadow-inner"
            style={{ backgroundColor: mapTheme.background }}
          >
            <MapContainer
              center={COLOMBIA_CENTER}
              zoom={6}
              scrollWheelZoom={false}
              zoomControl
              attributionControl={false}
              className="h-full w-full"
            >
              <MapFitColombiaLayer boundaryData={boundaryData} />

              {boundaryData ? (
                <>
                  <GeoJSON
                    data={boundaryData}
                    style={() => ({
                      color: mapTheme.background,
                      weight: 3,
                      fillColor: mapTheme.landFill,
                      fillOpacity: 1,
                    })}
                    interactive={false}
                  />
                  <GeoJSON
                    data={boundaryData}
                    style={() => ({
                      color: mapTheme.landStroke,
                      weight: mapTheme.landWeight,
                      fillColor: mapTheme.landFill,
                      fillOpacity: 1,
                    })}
                    interactive={false}
                  />
                </>
              ) : null}

              {(points as OutbreakMapPoint[]).map((point) => {
                const isSelected = point.territorial_code === selectedCode;
                const color = classificationColors[point.classification];
                return (
                  <CircleMarker
                    key={point.territorial_code}
                    center={[point.latitude, point.longitude]}
                    radius={isSelected ? 13 : 10}
                    pathOptions={{
                      color: isSelected ? mapTheme.selectedRing : mapTheme.markerStroke,
                      weight: isSelected ? 3 : mapTheme.markerStrokeWidth,
                      fillColor: color,
                      fillOpacity: 1,
                    }}
                    eventHandlers={{
                      click: () =>
                        onSelectMunicipality(point.territorial_code, point.municipality_name),
                    }}
                  >
                    <Tooltip
                      permanent={isSelected}
                      direction="top"
                      offset={[0, -14]}
                      className={isSelected ? "colombia-map-label" : undefined}
                    >
                      <span className="font-medium">
                        {formatMunicipalityName(point.municipality_name)}
                      </span>
                      {" · "}
                      {point.outbreak_probability.toFixed(0)}
                      {!isSelected ? (
                        <>
                          {" · "}
                          {point.observed_cases.toFixed(0)} casos
                        </>
                      ) : null}
                    </Tooltip>
                  </CircleMarker>
                );
              })}
            </MapContainer>
          </div>
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
