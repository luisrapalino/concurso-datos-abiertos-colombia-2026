import { TerritorialMapPanel } from "@/components/map/territorial-map-panel";

export default function MapaPage() {
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Mapa territorial</h2>
        <p className="mt-1 text-[var(--muted-foreground)]">
          Visualización geográfica del score de riesgo por territorio (centroides departamentales).
        </p>
      </div>
      <TerritorialMapPanel />
    </div>
  );
}
