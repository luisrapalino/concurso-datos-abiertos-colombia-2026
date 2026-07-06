"use client";

import { OutbreakAlertsPanel } from "@/components/outbreak/outbreak-alerts-panel";
import { PageHeader } from "@/components/shared/page-header";
import { QuickStartGuide } from "@/components/shared/quick-start-guide";

export default function RadarPage() {
  return (
    <div className="space-y-5">
      <PageHeader
        eyebrow="Vigilancia territorial"
        title="Prioridad territorial"
        description="Ranking de señales de brote en ciudades piloto. Empieza por el municipio con mayor señal o elige uno en los filtros."
      />
      <QuickStartGuide />
      <OutbreakAlertsPanel />
    </div>
  );
}
