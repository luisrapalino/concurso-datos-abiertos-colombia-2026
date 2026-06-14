"use client";

import Link from "next/link";
import {
  Activity,
  AlertTriangle,
  BarChart3,
  Lightbulb,
  Shield,
} from "lucide-react";
import { Badge, riskBadgeVariant, severityBadgeVariant } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { epidemiologicalApi } from "@/lib/api/client";
import { useApiResource } from "@/hooks/use-api-resource";
import { useTerritorialFilters } from "@/stores/territorial-filters";

const modules = [
  {
    href: "/indicadores",
    title: "Indicadores de salud",
    description: "Observaciones territoriales curadas desde datos abiertos.",
    icon: BarChart3,
  },
  {
    href: "/riesgo",
    title: "Riesgo territorial",
    description: "Score explicable frente a la mediana nacional.",
    icon: Shield,
  },
  {
    href: "/anomalias",
    title: "Detección de anomalías",
    description: "Alertas por desviaciones respecto a la línea base.",
    icon: AlertTriangle,
  },
  {
    href: "/tendencias",
    title: "Tendencias y proyección",
    description: "Serie histórica con extrapolación lineal.",
    icon: Activity,
  },
  {
    href: "/insights",
    title: "Insights narrativos",
    description: "Síntesis interpretable para toma de decisiones.",
    icon: Lightbulb,
  },
];

function DashboardSummary({
  territorialCode,
  period,
}: {
  territorialCode: string;
  period: string;
}) {
  const { data: risk, loading: riskLoading } = useApiResource(
    () => epidemiologicalApi.predictRisk({ territorial_code: territorialCode, period }),
    [territorialCode, period],
  );
  const { data: anomalies, loading: anomaliesLoading } = useApiResource(
    () =>
      epidemiologicalApi.listAnomalies({
        territorial_code: territorialCode,
        page: 1,
        page_size: 1,
      }),
    [territorialCode],
  );
  const { data: insights, loading: insightsLoading } = useApiResource(
    () => epidemiologicalApi.listInsights({ territorial_code: territorialCode, limit: 5 }),
    [territorialCode],
  );

  const loading = riskLoading || anomaliesLoading || insightsLoading;

  return (
    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <Card>
        <CardHeader className="pb-2">
          <CardDescription>Score de riesgo</CardDescription>
          <CardTitle className="text-3xl tabular-nums">
            {loading ? <Skeleton className="h-9 w-20" /> : risk?.score.toFixed(1) ?? "—"}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <Skeleton className="h-6 w-16" />
          ) : risk ? (
            <Badge variant={riskBadgeVariant(risk.classification)}>{risk.classification}</Badge>
          ) : (
            <span className="text-sm text-[var(--muted-foreground)]">Sin datos</span>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardDescription>Anomalías detectadas</CardDescription>
          <CardTitle className="text-3xl tabular-nums">
            {loading ? (
              <Skeleton className="h-9 w-12" />
            ) : (
              (anomalies?.total_items ?? 0)
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {!loading && (anomalies?.total_items ?? 0) > 0 ? (
            <Badge variant={severityBadgeVariant("medium")}>Revisar alertas</Badge>
          ) : (
            <span className="text-sm text-[var(--muted-foreground)]">
              Sin alertas activas
            </span>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardDescription>Insights generados</CardDescription>
          <CardTitle className="text-3xl tabular-nums">
            {loading ? <Skeleton className="h-9 w-12" /> : (insights?.length ?? 0)}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <span className="text-sm text-[var(--muted-foreground)]">
            Narrativa explicable disponible
          </span>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardDescription>Fuente de datos</CardDescription>
          <CardTitle className="text-lg">datos.gov.co</CardTitle>
        </CardHeader>
        <CardContent>
          <span className="text-sm text-[var(--muted-foreground)]">
            Mortalidad general INS · último año publicado 2020
          </span>
        </CardContent>
      </Card>
    </section>
  );
}

export default function HomePage() {
  const { territorialCode, period } = useTerritorialFilters();

  return (
    <div className="space-y-6">
      <section>
        <h2 className="text-2xl font-bold tracking-tight">Panel territorial</h2>
        <p className="mt-1 text-[var(--muted-foreground)]">
          Territorio <strong>{territorialCode}</strong> · Periodo{" "}
          <strong>{period}</strong>
        </p>
      </section>

      <DashboardSummary
        key={`${territorialCode}:${period}`}
        territorialCode={territorialCode}
        period={period}
      />

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {modules.map(({ href, title, description, icon: Icon }) => (
          <Link key={href} href={href} className="group">
            <Card className="h-full transition-shadow group-hover:shadow-md">
              <CardHeader>
                <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-md bg-[var(--primary)]/10 text-[var(--primary)]">
                  <Icon className="h-5 w-5" />
                </div>
                <CardTitle className="text-base">{title}</CardTitle>
                <CardDescription>{description}</CardDescription>
              </CardHeader>
            </Card>
          </Link>
        ))}
      </section>
    </div>
  );
}
