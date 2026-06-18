import { CompassIcon } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

const steps = [
  "Revisa el ranking y localiza municipios con señal elevada.",
  "Selecciona municipio y enfermedad en los filtros superiores.",
  "Abre la ficha, el mapa o el informe para profundizar el análisis.",
];

export function QuickStartGuide() {
  return (
    <Card size="sm" className="border-primary/20 bg-card/90">
      <CardContent className="flex gap-3 pt-4">
        <CompassIcon className="mt-0.5 size-4 shrink-0 text-primary" />
        <div className="min-w-0 space-y-2">
          <p className="text-sm font-medium text-foreground">Por dónde empezar</p>
          <ol className="grid gap-2 text-sm text-muted-foreground sm:grid-cols-3 sm:gap-4">
            {steps.map((step) => (
              <li key={step} className="flex gap-2">
                <span className="mt-1.5 size-1.5 shrink-0 rounded-full bg-primary" aria-hidden />
                <span>{step}</span>
              </li>
            ))}
          </ol>
        </div>
      </CardContent>
    </Card>
  );
}
