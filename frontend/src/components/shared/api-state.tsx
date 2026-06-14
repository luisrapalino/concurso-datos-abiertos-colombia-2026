"use client";

import { AlertCircle, Loader2 } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

export function LoadingState({ message = "Cargando datos..." }: { message?: string }) {
  return (
    <Card>
      <CardContent className="flex items-center gap-3 py-8 text-[var(--muted-foreground)]">
        <Loader2 className="h-5 w-5 animate-spin" />
        <span>{message}</span>
      </CardContent>
    </Card>
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
    <Card className="border-red-200 dark:border-red-900">
      <CardContent className="flex flex-col gap-3 py-8">
        <div className="flex items-start gap-3 text-red-700 dark:text-red-300">
          <AlertCircle className="mt-0.5 h-5 w-5 shrink-0" />
          <div>
            <p className="font-medium">No fue posible cargar la información</p>
            <p className="mt-1 text-sm opacity-90">{message}</p>
          </div>
        </div>
        {onRetry ? (
          <button
            type="button"
            onClick={onRetry}
            className="self-start text-sm font-medium text-[var(--primary)] hover:underline"
          >
            Reintentar
          </button>
        ) : null}
      </CardContent>
    </Card>
  );
}

export function EmptyState({ message }: { message: string }) {
  return (
    <Card>
      <CardContent className="py-8 text-center text-[var(--muted-foreground)]">
        {message}
      </CardContent>
    </Card>
  );
}
