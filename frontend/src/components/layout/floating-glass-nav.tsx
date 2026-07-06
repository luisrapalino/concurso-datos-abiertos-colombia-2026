"use client";

import Link from "next/link";
import { motion, useReducedMotion } from "motion/react";
import { cn } from "@/lib/utils";

export type FloatingNavLink =
  | { type: "route"; href: string; label: string }
  | { type: "anchor"; href: string; label: string };

type FloatingGlassNavProps = {
  brand?: React.ReactNode;
  links?: FloatingNavLink[];
  actions?: React.ReactNode;
  activeHref?: string;
  className?: string;
};

export function FloatingGlassNav({
  brand,
  links = [],
  actions,
  activeHref,
  className,
}: FloatingGlassNavProps) {
  const reduceMotion = useReducedMotion();

  return (
    <div
      data-floating-nav
      className={cn(
        "app-chrome pointer-events-none fixed inset-x-0 top-0 z-50 flex justify-center px-4 pt-4",
        className,
      )}
    >
      <motion.nav
        initial={reduceMotion ? false : { opacity: 0, y: -16, scale: 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
        className="liquid-glass pointer-events-auto flex w-full max-w-4xl items-center gap-2 rounded-full px-2 py-2 sm:gap-3 sm:px-3"
        aria-label="Navegación principal"
      >
        {brand ? <div className="flex shrink-0 items-center">{brand}</div> : null}

        {links.length > 0 ? (
          <div className="flex min-w-0 flex-1 items-center justify-center gap-0.5 overflow-x-auto px-1 scrollbar-none">
            {links.map((link) => {
              const isActive = link.type === "route" && activeHref === link.href;
              const linkClassName = cn(
                "liquid-glass-nav-link whitespace-nowrap",
                isActive && "liquid-glass-nav-link-active",
              );

              if (link.type === "anchor") {
                return (
                  <a key={link.href} href={link.href} className={linkClassName}>
                    {link.label}
                  </a>
                );
              }

              return (
                <Link key={link.href} href={link.href} className={linkClassName} data-active={isActive}>
                  {link.label}
                </Link>
              );
            })}
          </div>
        ) : (
          <div className="flex-1" />
        )}

        {actions ? <div className="flex shrink-0 items-center gap-1.5 sm:gap-2">{actions}</div> : null}
      </motion.nav>
    </div>
  );
}

/** Espacio superior para contenido bajo la barra flotante (derivado de --floating-nav-* en globals.css) */
export const FLOATING_NAV_OFFSET = "floating-nav-offset";

/** Hero de marketing: mismo cálculo con más aire bajo la píldora */
export const FLOATING_NAV_HERO_OFFSET = "floating-nav-hero-offset";
