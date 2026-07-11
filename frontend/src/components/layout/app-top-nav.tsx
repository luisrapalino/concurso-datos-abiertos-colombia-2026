"use client";

import Link from "next/link";
import { Bug } from "lucide-react";
import { usePathname } from "next/navigation";
import {
  FLOATING_NAV_OFFSET,
  FloatingGlassNav,
} from "@/components/layout/floating-glass-nav";
import { ThemeToggle } from "@/components/layout/theme-toggle";

const navItems = [
  { href: "/", label: "Inicio" },
  { href: "/radar", label: "Radar" },
  { href: "/brotes", label: "Ficha" },
  { href: "/mapa", label: "Mapa" },
  { href: "/informe", label: "Informe" },
  { href: "/datos", label: "Datos" },
] as const;

export function AppTopNav() {
  const pathname = usePathname();

  return (
    <FloatingGlassNav
      brand={
        <Link
          href="/radar"
          className="liquid-glass-brand flex items-center rounded-full p-1"
          aria-label="Radar de Brotes"
        >
          <span className="flex size-8 items-center justify-center rounded-full bg-primary/90 text-primary-foreground shadow-sm">
            <Bug className="size-3.5" />
          </span>
        </Link>
      }
      activeHref={pathname}
      links={navItems.map(({ href, label }) => ({ type: "route" as const, href, label }))}
      actions={<ThemeToggle variant="glass" />}
    />
  );
}

export { FLOATING_NAV_HERO_OFFSET, FLOATING_NAV_OFFSET } from "@/components/layout/floating-glass-nav";
