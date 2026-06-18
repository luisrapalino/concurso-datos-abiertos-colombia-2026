import { OutbreakReportPanel } from "@/components/report/outbreak-report-panel";
import { PageHeader } from "@/components/shared/page-header";

export default function InformePage() {
  return (
    <div className="space-y-5">
      <PageHeader
        eyebrow="Resumen para decisión"
        title="Informe territorial"
        description="Síntesis exportable con señal, factores y tendencia para compartir con equipos de vigilancia."
      />
      <OutbreakReportPanel />
    </div>
  );
}
