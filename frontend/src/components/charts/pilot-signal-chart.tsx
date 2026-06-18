"use client";

import type { OutbreakMapPoint } from "@/lib/api/types";
import {
  EChart,
  classificationColor,
  useChartTheme,
} from "@/components/charts/echarts-base";
import { formatMunicipalityName } from "@/lib/domain-labels";

interface PilotSignalChartProps {
  points: OutbreakMapPoint[];
  selectedCode?: string;
  height?: number;
}

export function PilotSignalChart({
  points,
  selectedCode,
  height = 240,
}: PilotSignalChartProps) {
  const colors = useChartTheme();

  if (!points.length) {
    return null;
  }

  const sorted = [...points].sort(
    (a, b) => b.outbreak_probability - a.outbreak_probability,
  );
  const labels = sorted.map((point) => formatMunicipalityName(point.municipality_name));
  const values = sorted.map((point) => point.outbreak_probability);
  const barColors = sorted.map((point) => {
    if (point.territorial_code === selectedCode) {
      return colors.selected;
    }
    return classificationColor(point.classification, colors);
  });

  return (
    <EChart
      height={height}
      option={{
        tooltip: {
          trigger: "axis",
          axisPointer: { type: "shadow" },
          formatter: (params) => {
            const item = Array.isArray(params) ? params[0] : params;
            const point = sorted[item.dataIndex];
            if (!point) return "";
            return [
              `<strong>${formatMunicipalityName(point.municipality_name)}</strong>`,
              `Señal: ${point.outbreak_probability.toFixed(1)}`,
              `Casos: ${point.observed_cases.toFixed(0)}`,
            ].join("<br/>");
          },
        },
        grid: { left: 8, right: 16, top: 16, bottom: 8, containLabel: true },
        xAxis: {
          type: "value",
          max: 100,
          name: "Señal",
          nameTextStyle: { fontSize: 11, color: colors.muted },
          splitLine: { lineStyle: { type: "dashed", color: colors.grid } },
          axisLabel: { color: colors.muted },
        },
        yAxis: {
          type: "category",
          data: labels,
          inverse: true,
          axisLabel: { fontSize: 12, color: colors.text },
        },
        series: [
          {
            type: "bar",
            data: values.map((value, index) => ({
              value,
              itemStyle: { color: barColors[index], borderRadius: [0, 4, 4, 0] },
            })),
            barMaxWidth: 28,
          },
        ],
      }}
    />
  );
}
