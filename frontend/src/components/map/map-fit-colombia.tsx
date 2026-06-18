"use client";

import { useEffect } from "react";
import { useMap } from "react-leaflet";
import type { GeoFeatureCollection } from "@/lib/api/types";
import { COLOMBIA_CENTER, COLOMBIA_BOUNDS } from "@/components/map/colombia-map-theme";

interface MapFitColombiaProps {
  boundaryData?: GeoFeatureCollection | null;
}

export function MapFitColombia({ boundaryData }: MapFitColombiaProps) {
  const map = useMap();

  useEffect(() => {
    map.setMaxBounds(COLOMBIA_BOUNDS);
    map.setMinZoom(5);

    if (boundaryData?.features?.length) {
      import("leaflet").then((L) => {
        const layer = L.geoJSON(boundaryData as never);
        const bounds = layer.getBounds();
        if (bounds.isValid()) {
          map.fitBounds(bounds, { padding: [24, 24], maxZoom: 6 });
        }
      });
      return;
    }

    map.fitBounds(COLOMBIA_BOUNDS, { padding: [24, 24], maxZoom: 6 });
  }, [map, boundaryData]);

  return null;
}
