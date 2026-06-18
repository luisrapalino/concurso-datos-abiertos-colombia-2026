"use client";

import type { ReactNode } from "react";
import { usePathname } from "next/navigation";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { fadeSlide, presenceTransition } from "@/lib/motion-presets";

export function PageTransition({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const reduceMotion = useReducedMotion();

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={pathname}
        initial={fadeSlide.initial}
        animate={fadeSlide.animate}
        exit={fadeSlide.exit}
        transition={presenceTransition(reduceMotion)}
        className="flex-1"
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}
