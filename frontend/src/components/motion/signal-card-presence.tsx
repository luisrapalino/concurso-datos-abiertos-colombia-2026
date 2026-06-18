"use client";

import type { ReactNode } from "react";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { PresenceShell } from "@/components/motion/presence-shell";
import { fadeSlide, presenceTransition } from "@/lib/motion-presets";

interface SignalCardPresenceProps {
  presenceKey: string | null;
  children: ReactNode;
}

export function SignalCardPresence({ presenceKey, children }: SignalCardPresenceProps) {
  const reduceMotion = useReducedMotion();
  const transition = presenceTransition(reduceMotion);

  return (
    <AnimatePresence mode="wait">
      {presenceKey ? (
        <motion.div
          key={presenceKey}
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
