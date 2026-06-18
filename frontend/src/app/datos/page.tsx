"use client";

import { DatasetsPanel } from "@/components/datasets/datasets-panel";
import { PageHeader } from "@/components/shared/page-header";

export default function DatosPage() {
  return (
    <div className="space-y-5">
      <PageHeader
        eyebrow="Trazabilidad"
        title="Fuentes de datos"
        description="Conjuntos abiertos por municipio: para cada variable se elige el mejor dataset disponible en datos.gov.co."
      />
      <DatasetsPanel />
    </div>
  );
}
