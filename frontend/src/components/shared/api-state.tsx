"use client";

import { AlertCircle, Inbox, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";

export function LoadingState({ message = "Cargando…" }: { message?: string }) {
  return (
    <div
      className="flex items-center gap-2.5 rounded-lg border border-border/60 bg-card/80 px-4 py-8 text-sm text-muted-foreground"
      role="status"
      aria-live="polite"
    >
      <Loader2 className="size-4 animate-spin text-primary" />
      <span>{message}</span>
    </div>
  );
}

export function ErrorState({
  message,
  onRetry,
}: {
  message: string;
  onRetry?: () => void;
}) {
  return (
    <div className="rounded-lg border border-destructive/25 bg-destructive/5 px-4 py-4 text-sm">
      <div className="flex items-start gap-3">
        <AlertCircle className="mt-0.5 size-4 shrink-0 text-destructive" />
        <div className="space-y-2">
          <p className="font-medium text-foreground">No se pudieron cargar los datos</p>
          <p className="text-muted-foreground">{message}</p>
          {onRetry ? (
            <Button type="button" variant="outline" size="sm" onClick={onRetry}>
              Reintentar
            </Button>
          ) : null}
        </div>
      </div>
    </div>
  );
}

export function EmptyState({
  message,
  hint,
}: {
  message: string;
  hint?: string;
}) {
  return (
    <div className="flex flex-col items-center gap-2 rounded-lg border border-dashed border-border bg-card/50 px-4 py-10 text-center">
      <Inbox className="size-5 text-muted-foreground/60" />
      <p className="text-sm font-medium text-foreground">{message}</p>
      {hint ? (
        <p className="max-w-sm text-xs text-muted-foreground">{hint}</p>
      ) : null}
    </div>
  );
}

export function LoadingSkeleton({ lines = 3 }: { lines?: number }) {
  return (
    <div className="space-y-2.5">
      {Array.from({ length: lines }).map((_, index) => (
        <Skeleton key={index} className="h-4 w-full" />
      ))}
    </div>
  );
}
