import { TrendPanel } from "@/components/trends/trend-panel";

export default function TendenciasPage() {
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Tendencias territoriales</h2>
        <p className="mt-1 text-[var(--muted-foreground)]">
          Evolución histórica y proyección lineal a corto plazo.
        </p>
      </div>
      <TrendPanel />
    </div>
  );
}
