"use client";

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
      activeHref={pathname}
      links={navItems.map(({ href, label }) => ({ type: "route" as const, href, label }))}
      actions={<ThemeToggle variant="glass" />}
    />
  );
}

export { FLOATING_NAV_HERO_OFFSET, FLOATING_NAV_OFFSET } from "@/components/layout/floating-glass-nav";
