import { Badge } from "@/components/ui/badge";
import { riskClassificationLabels } from "@/lib/domain-labels";
import { riskBadgeVariant } from "@/lib/risk-badges";
import { cn } from "@/lib/utils";

interface SignalReadoutProps {
  value: number;
  classification: string;
  label?: string;
  size?: "sm" | "lg";
  className?: string;
}

export function SignalReadout({
  value,
  classification,
  label = "Señal de brote",
  size = "lg",
  className,
}: SignalReadoutProps) {
  const isLarge = size === "lg";

  return (
    <div className={cn("flex items-center gap-3", className)}>
      <div
        className={cn(
          "signal-ring relative flex shrink-0 items-center justify-center rounded-full",
          isLarge ? "size-20" : "size-12",
        )}
        aria-hidden
      >
        <span
          className={cn(
            "font-mono font-semibold tabular-nums text-primary",
            isLarge ? "text-2xl" : "text-base",
          )}
        >
          {value.toFixed(1)}
        </span>
      </div>
      <div className="min-w-0 space-y-1">
        <p
          className={cn(
            "font-medium text-foreground",
            isLarge ? "text-sm" : "text-xs",
          )}
        >
          {label}
        </p>
        <Badge variant={riskBadgeVariant(classification)} className="text-xs">
          {riskClassificationLabels[classification] ?? classification}
        </Badge>
      </div>
    </div>
  );
}
