import { RiskPanel } from "@/components/risk/risk-panel";

export default function RiesgoPage() {
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Riesgo territorial</h2>
        <p className="mt-1 text-[var(--muted-foreground)]">
          Score normalizado y clasificación explicable frente a la mediana nacional.
        </p>
      </div>
      <RiskPanel />
    </div>
  );
}
