"use client";

import type { OutbreakFeatureContribution } from "@/lib/api/types";
import { outbreakFeatureLabels } from "@/lib/domain-labels";
import { EChart, useChartTheme } from "@/components/charts/echarts-base";

interface FeatureContributionsChartProps {
  contributions: OutbreakFeatureContribution[];
  height?: number;
}

export function FeatureContributionsChart({
  contributions,
  height = 220,
}: FeatureContributionsChartProps) {
  const colors = useChartTheme();

  if (!contributions.length) {
    return null;
  }

  const sorted = [...contributions].sort((a, b) => b.contribution - a.contribution);
  const labels = sorted.map(
    (item) => outbreakFeatureLabels[item.feature] ?? item.feature,
  );
  const values = sorted.map((item) => item.contribution);

  return (
    <EChart
      height={height}
      option={{
        tooltip: {
          trigger: "axis",
          axisPointer: { type: "shadow" },
          valueFormatter: (value) => `${Number(value).toFixed(1)} pts`,
        },
        grid: { left: 8, right: 24, top: 8, bottom: 8, containLabel: true },
        xAxis: {
          type: "value",
          max: 100,
          splitLine: { lineStyle: { type: "dashed", color: colors.grid } },
          axisLabel: { color: colors.muted },
        },
        yAxis: {
          type: "category",
          data: labels,
          axisLabel: { fontSize: 11, width: 140, overflow: "truncate", color: colors.text },
        },
        series: [
          {
            type: "bar",
            data: values,
            itemStyle: { color: colors.primary, borderRadius: [0, 4, 4, 0] },
            barMaxWidth: 20,
          },
        ],
      }}
    />
  );
}
