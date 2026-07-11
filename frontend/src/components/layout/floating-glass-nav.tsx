"use client";

import Link from "next/link";
import { Menu } from "lucide-react";
import { motion, useReducedMotion } from "motion/react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
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

function NavLinkItem({
  link,
  activeHref,
  className,
  onNavigate,
}: {
  link: FloatingNavLink;
  activeHref?: string;
  className?: string;
  onNavigate?: () => void;
}) {
  const isActive = link.type === "route" && activeHref === link.href;
  const linkClassName = cn(
    "liquid-glass-nav-link",
    isActive && "liquid-glass-nav-link-active",
    className,
  );

  if (link.type === "anchor") {
    return (
      <a href={link.href} className={linkClassName} onClick={onNavigate}>
        {link.label}
      </a>
    );
  }

  return (
    <Link
      href={link.href}
      className={linkClassName}
      data-active={isActive}
      onClick={onNavigate}
    >
      {link.label}
    </Link>
  );
}

function MobileNavMenu({
  links,
  activeHref,
}: {
  links: FloatingNavLink[];
  activeHref?: string;
}) {
  const [open, setOpen] = useState(false);
  const closeMenu = () => setOpen(false);

  return (
    <>
      <Button
        type="button"
        variant="ghost"
        size="icon"
        className="size-8 shrink-0 rounded-full border-0 text-muted-foreground hover:bg-(--glass-nav-hover) hover:text-foreground md:hidden"
        aria-label={open ? "Cerrar menú" : "Abrir menú"}
        aria-expanded={open}
        onClick={() => setOpen(true)}
      >
        <Menu className="size-4" />
      </Button>

      <Sheet open={open} onOpenChange={setOpen}>
        <SheetContent
          side="right"
          className="w-[min(100vw-2rem,20rem)] border-border/40 p-0 sm:max-w-xs"
        >
          <div className="liquid-glass-subtle flex h-full flex-col">
            <SheetHeader className="border-b border-border/30 px-5 py-4">
              <SheetTitle className="font-heading text-base">Menú</SheetTitle>
            </SheetHeader>
            <nav
              className="flex flex-col gap-1 p-3"
              aria-label="Navegación móvil"
            >
              {links.map((link) => {
                const isActive = link.type === "route" && activeHref === link.href;

                return (
                  <NavLinkItem
                    key={link.href}
                    link={link}
                    activeHref={activeHref}
                    onNavigate={closeMenu}
                    className={cn(
                      "w-full rounded-xl px-4 py-3 text-left text-base",
                      isActive && "liquid-glass-nav-link-active",
                    )}
                  />
                );
              })}
            </nav>
          </div>
        </SheetContent>
      </Sheet>
    </>
  );
}

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
        className="liquid-glass pointer-events-auto flex w-full max-w-4xl items-center gap-1.5 rounded-full px-2 py-2 sm:gap-3 sm:px-3"
        aria-label="Navegación principal"
      >
        {brand ? <div className="flex shrink-0 items-center">{brand}</div> : null}

        {links.length > 0 ? (
          <>
            <div className="hidden min-w-0 flex-1 items-center justify-center gap-0.5 overflow-x-auto px-1 scrollbar-none md:flex">
              {links.map((link) => (
                <NavLinkItem key={link.href} link={link} activeHref={activeHref} />
              ))}
            </div>
            <div className="flex-1 md:hidden" />
            <MobileNavMenu links={links} activeHref={activeHref} />
          </>
        ) : (
          <div className="flex-1" />
        )}

        {actions ? (
          <div className="flex shrink-0 items-center gap-1 sm:gap-2">{actions}</div>
        ) : null}
      </motion.nav>
    </div>
  );
}

/** Espacio superior para contenido bajo la barra flotante (derivado de --floating-nav-* en globals.css) */
export const FLOATING_NAV_OFFSET = "floating-nav-offset";

/** Hero de marketing: mismo cálculo con más aire bajo la píldora */
export const FLOATING_NAV_HERO_OFFSET = "floating-nav-hero-offset";
