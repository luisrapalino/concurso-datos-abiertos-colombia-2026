"use client";

import { PageHeader } from "@/components/shared/page-header";
import { OutbreakPanel } from "@/components/outbreak/outbreak-panel";

export default function BrotesPage() {
  return (
    <div className="space-y-5">
      <PageHeader
        eyebrow="Análisis municipal"
        title="Ficha territorial"
        description="Señal de brote, factores explicativos y tendencia semanal del municipio seleccionado."
      />
      <OutbreakPanel />
    </div>
  );
}
