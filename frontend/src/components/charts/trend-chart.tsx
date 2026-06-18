"use client";

import type { TerritorialTrend } from "@/lib/api/types";
import { EChart, useChartTheme } from "@/components/charts/echarts-base";

interface TrendChartProps {
  trend: TerritorialTrend;
  height?: number;
}

export function TrendChart({ trend, height = 300 }: TrendChartProps) {
  const colors = useChartTheme();

  const historical = trend.points.filter((point) => point.kind === "historical");
  const forecast = trend.points.filter((point) => point.kind === "forecast");

  const categories = trend.points.map((point) => point.period);
  const historicalValues = trend.points.map((point) =>
    point.kind === "historical" ? point.value : null,
  );
  const forecastValues = trend.points.map((point) =>
    point.kind === "forecast" ? point.value : null,
  );

  if (historical.length > 0 && forecast.length > 0) {
    const lastHistorical = historical[historical.length - 1];
    const bridgeIndex = categories.indexOf(lastHistorical.period);
    if (bridgeIndex >= 0) {
      forecastValues[bridgeIndex] = lastHistorical.value;
    }
  }

  return (
    <EChart
      height={height}
      option={{
        tooltip: { trigger: "axis" },
        legend: {
          data: ["Histórico", "Proyección"],
          bottom: 0,
          textStyle: { fontSize: 11, color: colors.text },
        },
        grid: { left: 48, right: 16, top: 24, bottom: 48 },
        xAxis: {
          type: "category",
          data: categories,
          axisLabel: { rotate: 35, fontSize: 10, color: colors.muted },
        },
        yAxis: {
          type: "value",
          name: "Casos",
          nameTextStyle: { fontSize: 11, color: colors.muted },
          axisLabel: { color: colors.muted },
          splitLine: { lineStyle: { type: "dashed", color: colors.grid } },
        },
        series: [
          {
            name: "Histórico",
            type: "line",
            data: historicalValues,
            smooth: true,
            lineStyle: { width: 2, color: colors.primary },
            itemStyle: { color: colors.primary },
            areaStyle: { color: colors.area },
          },
          {
            name: "Proyección",
            type: "line",
            data: forecastValues,
            smooth: true,
            lineStyle: { type: "dashed", width: 2, color: colors.forecast },
            itemStyle: { color: colors.forecast },
          },
        ],
      }}
    />
  );
}
