import { TerritorialMapPanel } from "@/components/map/territorial-map-panel";
import { PageHeader } from "@/components/shared/page-header";

export default function MapaPage() {
  return (
    <div className="space-y-5">
      <PageHeader
        eyebrow="Distribución geográfica"
        title="Mapa territorial"
        description="Ubicación y clasificación de riesgo por municipio según la señal epidemiológica activa."
      />
      <TerritorialMapPanel />
    </div>
  );
}
