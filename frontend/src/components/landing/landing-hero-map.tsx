"use client";

import { useState } from "react";
import { ColombiaTerritorialChart } from "@/components/map/colombia-territorial-chart";
import { Skeleton } from "@/components/ui/skeleton";
import { useApiResource } from "@/hooks/use-api-resource";
import { epidemiologicalApi } from "@/lib/api/client";
import type { GeoFeatureCollection, OutbreakMapPoint } from "@/lib/api/types";
import { DEFAULT_FEATURED_MUNICIPALITY } from "@/lib/featured-municipalities";
import { DEFAULT_EVENT_CODE } from "@/lib/sivigila-events";

const DEFAULT_PERIOD = "2022-W01";

export function LandingHeroMap() {
  const [selectedCode, setSelectedCode] = useState(DEFAULT_FEATURED_MUNICIPALITY.territorial_code);

  const outbreakQuery = useApiResource(
    () =>
      epidemiologicalApi.listOutbreakMap({
        period: DEFAULT_PERIOD,
        event_code: DEFAULT_EVENT_CODE,
        featured_only: true,
      }),
    [],
  );
  const boundariesQuery = useApiResource(
    () => epidemiologicalApi.getTerritorialBoundaries("department"),
    [],
  );

  const points = outbreakQuery.data;
  const boundaryData = boundariesQuery.data as GeoFeatureCollection | null;
  const loading = outbreakQuery.loading || boundariesQuery.loading;
  const error = outbreakQuery.error ?? boundariesQuery.error;

  return (
    <div className="relative mx-auto w-full max-w-xl aspect-4/5 md:aspect-5/6 lg:max-w-2xl">
      <div className="landing-glow pointer-events-none absolute inset-4 rounded-full blur-3xl md:inset-6" aria-hidden />

      {loading ? (
        <Skeleton
          className="absolute inset-0 rounded-full bg-primary/5"
          aria-busy
          aria-label="Cargando mapa"
        />
      ) : error || !points?.length ? (
        <p
          className="absolute inset-0 flex items-center justify-center px-6 text-center text-xs text-muted-foreground"
          role="status"
        >
          {error ?? "Mapa no disponible"}
        </p>
      ) : (
        <ColombiaTerritorialChart
          embedded
          boundaryData={boundaryData}
          points={points as OutbreakMapPoint[]}
          selectedCode={selectedCode}
          height="100%"
          className="absolute inset-0 bg-transparent"
          onSelectMunicipality={(code) => setSelectedCode(code)}
        />
      )}
    </div>
  );
}
