"use client";

import { Badge } from "@/components/ui/badge";
import { confidenceBadgeVariant } from "@/lib/risk-badges";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  EmptyState,
  ErrorState,
  LoadingState,
} from "@/components/shared/api-state";
import { epidemiologicalApi } from "@/lib/api/client";
import { useApiResource } from "@/hooks/use-api-resource";
import { useTerritorialFilters } from "@/stores/territorial-filters";

const confidenceLabels: Record<string, string> = {
  low: "Baja",
  medium: "Media",
  high: "Alta",
};

function InsightCardsContent({ territorialCode }: { territorialCode: string }) {
  const { data, error, loading, reload } = useApiResource(
    () => epidemiologicalApi.listInsights({ territorial_code: territorialCode, limit: 5 }),
    [territorialCode],
  );

  if (loading) return <LoadingState message="Generando insights..." />;
  if (error) return <ErrorState message={error} onRetry={reload} />;

  const items = data ?? [];
  if (items.length === 0) {
    return (
      <EmptyState message="No hay insights narrativos para el territorio seleccionado." />
    );
  }

  return (
    <div className="grid gap-4">
      {items.map((insight) => (
        <Card key={insight.id}>
          <CardHeader>
            <div className="flex flex-wrap items-center gap-2">
              <CardTitle className="text-base">{insight.title}</CardTitle>
              <Badge variant={confidenceBadgeVariant(insight.confidence)}>
                Confianza {confidenceLabels[insight.confidence] ?? insight.confidence}
              </Badge>
            </div>
            <CardDescription>
              Versión {insight.data_version} · Territorio {insight.territorial_code}
              {insight.analysis_period ? ` · Periodo ${insight.analysis_period}` : ""}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <p className="leading-relaxed text-[var(--foreground)]">{insight.narrative}</p>
            {insight.system_context ? (
              <p className="rounded-md border border-[var(--border)] bg-[var(--muted)]/40 p-2 text-xs text-[var(--muted-foreground)]">
                {insight.system_context}
              </p>
            ) : null}
            <p className="text-[var(--muted-foreground)]">
              Fuentes: {insight.sources.join(", ")}
            </p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

export function InsightCards() {
  const { territorialCode } = useTerritorialFilters();

  return <InsightCardsContent key={territorialCode} territorialCode={territorialCode} />;
}
