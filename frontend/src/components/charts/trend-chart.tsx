"use client";

import dynamic from "next/dynamic";
import type { TerritorialTrend } from "@/lib/api/types";

const ReactECharts = dynamic(() => import("echarts-for-react"), { ssr: false });

interface TrendChartProps {
  trend: TerritorialTrend;
}

export function TrendChart({ trend }: TrendChartProps) {
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

  const option = {
    tooltip: { trigger: "axis" as const },
    legend: {
      data: ["Histórico", "Proyección"],
      bottom: 0,
    },
    grid: { left: 48, right: 24, top: 24, bottom: 48 },
    xAxis: {
      type: "category" as const,
      data: categories,
      axisLabel: { rotate: 35 },
    },
    yAxis: {
      type: "value" as const,
      name: trend.indicator_name,
    },
    series: [
      {
        name: "Histórico",
        type: "line" as const,
        data: historicalValues,
        smooth: true,
        lineStyle: { width: 2, color: "#0f766e" },
        itemStyle: { color: "#0f766e" },
      },
      {
        name: "Proyección",
        type: "line" as const,
        data: forecastValues,
        smooth: true,
        lineStyle: { type: "dashed" as const, width: 2, color: "#d97706" },
        itemStyle: { color: "#d97706" },
      },
    ],
  };

  return (
    <ReactECharts
      option={option}
      style={{ height: 360, width: "100%" }}
      opts={{ renderer: "svg" }}
    />
  );
}
