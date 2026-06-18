import type { VariantProps } from "class-variance-authority";

import { badgeVariants } from "@/components/ui/badge";

type BadgeVariant = NonNullable<VariantProps<typeof badgeVariants>["variant"]>;

export function riskBadgeVariant(classification: string): BadgeVariant {
  switch (classification) {
    case "critical":
    case "high":
      return "destructive";
    case "medium":
      return "secondary";
    case "low":
      return "outline";
    default:
      return "secondary";
  }
}

export function confidenceBadgeVariant(confidence: string): BadgeVariant {
  switch (confidence) {
    case "high":
      return "default";
    case "medium":
      return "secondary";
    case "low":
      return "outline";
    default:
      return "secondary";
  }
}

export function severityBadgeVariant(severity: string): BadgeVariant {
  switch (severity) {
    case "high":
      return "destructive";
    case "medium":
      return "secondary";
    case "low":
      return "outline";
    default:
      return "secondary";
  }
}
