import { AnomalyList } from "@/components/anomalies/anomaly-list";

export default function AnomaliasPage() {
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Anomalías</h2>
        <p className="mt-1 text-[var(--muted-foreground)]">
          Alertas territoriales por desviaciones significativas en mortalidad general.
        </p>
      </div>
      <AnomalyList />
    </div>
  );
}
