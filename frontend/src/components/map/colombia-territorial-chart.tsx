"use client";

import dynamic from "next/dynamic";
import * as echarts from "echarts";
import type { EChartsOption } from "echarts";
import { useEffect, useMemo } from "react";
import {
  COLOMBIA_BOUNDS_GEO,
  COLOMBIA_MAP_NAME,
  type MapClassification,
} from "@/components/map/colombia-map-theme";
import { useMapTheme } from "@/hooks/use-map-theme";
import type { GeoFeatureCollection, OutbreakMapPoint } from "@/lib/api/types";
import { formatMunicipalityName } from "@/lib/domain-labels";

const ReactECharts = dynamic(() => import("echarts-for-react"), { ssr: false });

interface ScatterDatum {
  name: string;
  value: [number, number];
  territorialCode: string;
  municipalityName: string;
  probability: number;
  observedCases: number;
  classification: MapClassification;
  isSelected: boolean;
  symbolSize: number;
  itemStyle: {
    color: string;
    borderColor: string;
    borderWidth: number;
  };
  label: {
    show: boolean;
  };
}

interface ColombiaTerritorialChartProps {
  boundaryData?: GeoFeatureCollection | null;
  points: OutbreakMapPoint[];
  selectedCode: string;
  height?: number;
  onSelectMunicipality: (code: string, name: string) => void;
}

function buildScatterData(
  points: OutbreakMapPoint[],
  selectedCode: string,
  classificationColors: Record<MapClassification, string>,
  mapTheme: ReturnType<typeof useMapTheme>["theme"],
): ScatterDatum[] {
  return points.map((point) => {
    const isSelected = point.territorial_code === selectedCode;
    const classification = point.classification as MapClassification;
    return {
      name: formatMunicipalityName(point.municipality_name),
      value: [point.longitude, point.latitude],
      territorialCode: point.territorial_code,
      municipalityName: point.municipality_name,
      probability: point.outbreak_probability,
      observedCases: point.observed_cases,
      classification,
      isSelected,
      symbolSize: isSelected ? 26 : 20,
      itemStyle: {
        color: classificationColors[classification],
        borderColor: isSelected ? mapTheme.selectedRing : mapTheme.markerStroke,
        borderWidth: isSelected ? 3 : mapTheme.markerStrokeWidth,
      },
      label: { show: isSelected },
    };
  });
}

export function ColombiaTerritorialChart({
  boundaryData,
  points,
  selectedCode,
  height = 440,
  onSelectMunicipality,
}: ColombiaTerritorialChartProps) {
  const { theme: mapTheme, classificationColors } = useMapTheme();
  const hasBoundaryMap = Boolean(boundaryData?.features?.length);

  useEffect(() => {
    if (!hasBoundaryMap || !boundaryData) return;
    echarts.registerMap(COLOMBIA_MAP_NAME, boundaryData as never);
  }, [boundaryData, hasBoundaryMap]);

  const scatterData = useMemo(
    () => buildScatterData(points, selectedCode, classificationColors, mapTheme),
    [classificationColors, mapTheme, points, selectedCode],
  );

  const option = useMemo<EChartsOption>(
    () => ({
      backgroundColor: mapTheme.background,
      tooltip: {
        trigger: "item",
        backgroundColor: mapTheme.tooltipBg,
        borderColor: mapTheme.tooltipBorder,
        borderWidth: 1,
        padding: [6, 10],
        textStyle: {
          color: mapTheme.tooltipText,
          fontSize: 11,
          fontFamily: "var(--font-dm-sans), system-ui, sans-serif",
        },
        extraCssText: "border-radius: 6px; box-shadow: 0 1px 4px rgb(20 40 36 / 0.12);",
        formatter: (params) => {
          if (!params || typeof params !== "object" || !("data" in params)) return "";
          const datum = params.data as ScatterDatum | undefined;
          if (!datum) return "";
          const cases =
            datum.isSelected
              ? ""
              : ` · <span style="color:${mapTheme.tooltipMuted}">${datum.observedCases.toFixed(0)} casos</span>`;
          return [
            `<span style="font-weight:500">${datum.name}</span>`,
            ` · ${datum.probability.toFixed(0)}${cases}`,
          ].join("");
        },
      },
      geo: {
        map: hasBoundaryMap ? COLOMBIA_MAP_NAME : undefined,
        boundingCoords: COLOMBIA_BOUNDS_GEO,
        roam: false,
        silent: true,
        layoutCenter: ["50%", "52%"],
        layoutSize: "100%",
        itemStyle: {
          areaColor: mapTheme.landFill,
          borderColor: mapTheme.landStroke,
          borderWidth: mapTheme.landWeight,
        },
        emphasis: {
          disabled: true,
        },
      },
      series: [
        {
          type: "scatter",
          coordinateSystem: "geo",
          data: scatterData,
          symbol: "circle",
          symbolSize: (value, params) => (params.data as ScatterDatum).symbolSize,
          itemStyle: {
            shadowBlur: 4,
            shadowColor: "rgba(20, 40, 36, 0.15)",
          },
          label: {
            show: true,
            formatter: (params) => {
              const datum = params.data as ScatterDatum;
              return datum.isSelected ? datum.name : "";
            },
            position: "top",
            distance: 6,
            color: mapTheme.tooltipText,
            fontSize: 11,
            fontWeight: 500,
            backgroundColor: mapTheme.tooltipBg,
            borderColor: mapTheme.tooltipBorder,
            borderWidth: 1,
            borderRadius: 4,
            padding: [2, 6],
          },
          emphasis: {
            scale: 1.08,
            itemStyle: {
              shadowBlur: 8,
              shadowColor: "rgba(20, 40, 36, 0.22)",
            },
          },
          zlevel: 2,
        },
      ],
    }),
    [classificationColors, hasBoundaryMap, mapTheme, scatterData],
  );

  return (
    <div
      className="colombia-map overflow-hidden rounded-lg border border-border/60 shadow-inner"
      style={{ height, backgroundColor: mapTheme.background }}
    >
      <ReactECharts
        option={option}
        style={{ height: "100%", width: "100%" }}
        opts={{ renderer: "svg" }}
        notMerge
        lazyUpdate
        onEvents={{
          click: (params: { data?: ScatterDatum }) => {
            const datum = params.data;
            if (!datum?.territorialCode) return;
            onSelectMunicipality(datum.territorialCode, datum.municipalityName);
          },
        }}
      />
    </div>
  );
}
