import { InsightCards } from "@/components/insights/insight-cards";

export default function InsightsPage() {
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Insights</h2>
        <p className="mt-1 text-[var(--muted-foreground)]">
          Narrativa analítica automática combinando riesgo, anomalías y tendencias.
        </p>
      </div>
      <InsightCards />
    </div>
  );
}
