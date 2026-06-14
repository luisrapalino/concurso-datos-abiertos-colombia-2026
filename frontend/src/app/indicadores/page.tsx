import { IndicatorTable } from "@/components/health-indicators/indicator-table";

export default function IndicadoresPage() {
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Indicadores de salud</h2>
        <p className="mt-1 text-[var(--muted-foreground)]">
          Observaciones territoriales curadas a partir de datos abiertos del INS.
        </p>
      </div>
      <IndicatorTable />
    </div>
  );
}
