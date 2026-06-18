"use client";

import type { ReactNode } from "react";
import { motion, useIsPresent } from "motion/react";

export function PresenceShell({ children }: { children: ReactNode }) {
  const isPresent = useIsPresent();

  return (
    <motion.div
      aria-hidden={!isPresent}
      className={isPresent ? undefined : "pointer-events-none"}
    >
      {children}
    </motion.div>
  );
}
