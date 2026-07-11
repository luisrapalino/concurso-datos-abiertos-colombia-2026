"use client";

import Link from "next/link";
import { ArrowRight, Bug } from "lucide-react";
import { FloatingGlassNav } from "@/components/layout/floating-glass-nav";
import { ThemeToggle } from "@/components/layout/theme-toggle";
import { Button } from "@/components/ui/button";

const LANDING_LINKS = [
  { type: "anchor" as const, href: "#capacidades", label: "Capacidades" },
  { type: "anchor" as const, href: "#datos", label: "Fuentes" },
  { type: "anchor" as const, href: "#metodo", label: "Método" },
];

export function LandingNav() {
  return (
    <FloatingGlassNav
      brand={
        <Link href="/" className="liquid-glass-brand flex items-center gap-2.5 rounded-full py-1 pr-2 pl-1.5">
          <span className="flex size-8 items-center justify-center rounded-full bg-primary/90 text-primary-foreground shadow-sm">
            <Bug className="size-3.5" />
          </span>
          <span className="hidden leading-tight sm:block">
            <span className="block font-heading text-sm font-semibold">Radar de Brotes</span>
            <span className="block text-[10px] text-muted-foreground">Colombia · datos abiertos</span>
          </span>
        </Link>
      }
      links={LANDING_LINKS}
      actions={
        <>
          <ThemeToggle variant="glass" />
          <Button
            render={<Link href="/radar" />}
            size="sm"
            className="h-8 gap-1.5 rounded-full px-3 sm:px-3.5"
          >
            <span className="hidden min-[380px]:inline">Entrar</span>
            <ArrowRight className="size-3.5" />
          </Button>
        </>
      }
    />
  );
}
