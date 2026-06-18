"use client";

import dynamic from "next/dynamic";
import type { EChartsOption } from "echarts";
import { useIsDark } from "@/hooks/use-is-dark";

export const ReactECharts = dynamic(() => import("echarts-for-react"), { ssr: false });

interface EChartProps {
  option: EChartsOption;
  height?: number;
  className?: string;
}

export function EChart({ option, height = 280, className }: EChartProps) {
  return (
    <div className={className}>
      <ReactECharts
        option={option}
        style={{ height, width: "100%" }}
        opts={{ renderer: "svg" }}
      />
    </div>
  );
}

export const chartColorsLight = {
  primary: "#0a5c54",
  forecast: "#b45309",
  muted: "#5c6f6b",
  high: "#b42318",
  medium: "#b45309",
  low: "#0a5c54",
  grid: "#c8d9d4",
  selected: "#0a5c54",
  area: "rgba(10, 92, 84, 0.1)",
  text: "#142824",
} as const;

export const chartColorsDark = {
  primary: "#2dd4bf",
  forecast: "#fbbf24",
  muted: "#94b8ad",
  high: "#f87171",
  medium: "#fbbf24",
  low: "#2dd4bf",
  grid: "#1f3d37",
  selected: "#2dd4bf",
  area: "rgba(45, 212, 191, 0.12)",
  text: "#e8f5f1",
} as const;

export interface ChartColors {
  primary: string;
  forecast: string;
  muted: string;
  high: string;
  medium: string;
  low: string;
  grid: string;
  selected: string;
  area: string;
  text: string;
}

/** @deprecated Usa useChartTheme() en componentes cliente */
export const chartColors = chartColorsLight;

export function useChartTheme(): ChartColors {
  const isDark = useIsDark();
  return isDark ? chartColorsDark : chartColorsLight;
}

export function classificationColor(classification: string, colors: ChartColors): string {
  switch (classification) {
    case "critical":
    case "high":
      return colors.high;
    case "medium":
      return colors.medium;
    default:
      return colors.low;
  }
}
