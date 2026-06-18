"use client";

import type { ReactNode } from "react";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { PresenceShell } from "@/components/motion/presence-shell";
import {
  EmptyState,
  ErrorState,
  LoadingState,
} from "@/components/shared/api-state";
import { fadeSlide, presenceTransition } from "@/lib/motion-presets";

export type ResourcePresenceState = "loading" | "error" | "empty" | "ready";

interface ResourcePresenceProps {
  state: ResourcePresenceState;
  loadingMessage?: string;
  errorMessage?: string;
  onRetry?: () => void;
  emptyMessage?: string;
  emptyHint?: string;
  children: ReactNode;
}

export function ResourcePresence({
  state,
  loadingMessage = "Cargando…",
  errorMessage,
  onRetry,
  emptyMessage = "Sin datos disponibles",
  emptyHint,
  children,
}: ResourcePresenceProps) {
  const reduceMotion = useReducedMotion();
  const transition = presenceTransition(reduceMotion);

  return (
    <AnimatePresence mode="wait">
      {state === "loading" ? (
        <motion.div
          key="loading"
          initial={fadeSlide.initial}
          animate={fadeSlide.animate}
          exit={fadeSlide.exit}
          transition={transition}
        >
          <PresenceShell>
            <LoadingState message={loadingMessage} />
          </PresenceShell>
        </motion.div>
      ) : null}

      {state === "error" && errorMessage ? (
        <motion.div
          key="error"
          initial={fadeSlide.initial}
          animate={fadeSlide.animate}
          exit={fadeSlide.exit}
          transition={transition}
        >
          <PresenceShell>
            <ErrorState message={errorMessage} onRetry={onRetry} />
          </PresenceShell>
        </motion.div>
      ) : null}

      {state === "empty" ? (
        <motion.div
          key="empty"
          initial={fadeSlide.initial}
          animate={fadeSlide.animate}
          exit={fadeSlide.exit}
          transition={transition}
        >
          <PresenceShell>
            <EmptyState message={emptyMessage} hint={emptyHint} />
          </PresenceShell>
        </motion.div>
      ) : null}

      {state === "ready" ? (
        <motion.div
          key="ready"
          initial={fadeSlide.initial}
          animate={fadeSlide.animate}
          exit={fadeSlide.exit}
          transition={transition}
        >
          <PresenceShell>{children}</PresenceShell>
        </motion.div>
      ) : null}
    </AnimatePresence>
  );
}
