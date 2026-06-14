"use client";

import dynamic from "next/dynamic";
import { useMemo } from "react";
import {
  EmptyState,
  ErrorState,
  LoadingState,
} from "@/components/shared/api-state";
import { epidemiologicalApi } from "@/lib/api/client";
import type { RiskClassification, TerritorialRiskMapPoint, GeoFeatureCollection } from "@/lib/api/types";
import { useApiResource } from "@/hooks/use-api-resource";
import { useTerritorialFilters } from "@/stores/territorial-filters";

const MapContainer = dynamic(
  async () => (await import("react-leaflet")).MapContainer,
  { ssr: false },
);
const TileLayer = dynamic(async () => (await import("react-leaflet")).TileLayer, {
  ssr: false,
});
const CircleMarker = dynamic(
  async () => (await import("react-leaflet")).CircleMarker,
  { ssr: false },
);
const Popup = dynamic(async () => (await import("react-leaflet")).Popup, { ssr: false });
const GeoJSON = dynamic(async () => (await import("react-leaflet")).GeoJSON, {
  ssr: false,
});

const classificationColors: Record<RiskClassification, string> = {
  low: "#059669",
  medium: "#d97706",
  high: "#dc2626",
  critical: "#7f1d1d",
};

function TerritorialMapContent({ period }: { period: string }) {
  const {
    data: points,
    error: pointsError,
    loading: pointsLoading,
    reload: reloadPoints,
  } = useApiResource(
    () => epidemiologicalApi.listTerritorialRiskMap({ period, limit: 200 }),
    [period],
  );
  const {
    data: boundaries,
    error: boundariesError,
    loading: boundariesLoading,
  } = useApiResource(() => epidemiologicalApi.getTerritorialBoundaries("department"), []);

  const loading = pointsLoading || boundariesLoading;
  const error = pointsError ?? boundariesError;

  const boundaryData = useMemo(
    () => boundaries as GeoFeatureCollection | null,
    [boundaries],
  );

  if (loading) return <LoadingState message="Construyendo mapa de riesgo..." />;
  if (error) return <ErrorState message={error} onRetry={reloadPoints} />;
  if (!points || points.length === 0) {
    return <EmptyState message="No hay puntos territoriales para el periodo seleccionado." />;
  }

  return (
    <div className="space-y-3">
      <p className="text-sm text-[var(--muted-foreground)]">
        {points.length} municipios con score de riesgo · coordenadas DIVIPOLA · contorno
        departamental DANE MGN 2018
      </p>
      <div className="h-[480px] overflow-hidden rounded-lg border border-[var(--border)]">
        <MapContainer
          center={[4.5709, -74.2973]}
          zoom={5}
          scrollWheelZoom
          className="h-full w-full"
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {boundaryData ? (
            <GeoJSON
              data={boundaryData}
              style={() => ({
                color: "#64748b",
                weight: 1,
                fillColor: "#e2e8f0",
                fillOpacity: 0.15,
              })}
            />
          ) : null}
          {points.map((point: TerritorialRiskMapPoint) => (
            <CircleMarker
              key={point.territorial_code}
              center={[point.latitude, point.longitude]}
              radius={6}
              pathOptions={{
                color: classificationColors[point.classification],
                fillColor: classificationColors[point.classification],
                fillOpacity: 0.85,
              }}
            >
              <Popup>
                <strong>{point.territorial_code}</strong>
                <br />
                Score: {point.score.toFixed(1)} ({point.classification})
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>
      </div>
    </div>
  );
}

export function TerritorialMapPanel() {
  const { period } = useTerritorialFilters();

  return <TerritorialMapContent key={period} period={period} />;
}
