"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  AlertTriangle,
  BarChart3,
  Home,
  Lightbulb,
  Map,
  Shield,
} from "lucide-react";
import { cn } from "@/lib/utils/cn";

const navItems = [
  { href: "/", label: "Inicio", icon: Home },
  { href: "/indicadores", label: "Indicadores", icon: BarChart3 },
  { href: "/mapa", label: "Mapa territorial", icon: Map },
  { href: "/riesgo", label: "Riesgo territorial", icon: Shield },
  { href: "/anomalias", label: "Anomalías", icon: AlertTriangle },
  { href: "/tendencias", label: "Tendencias", icon: Activity },
  { href: "/insights", label: "Insights", icon: Lightbulb },
];

export function NavBar() {
  const pathname = usePathname();

  return (
    <nav className="flex flex-col gap-1">
      {navItems.map(({ href, label, icon: Icon }) => {
        const active = pathname === href;

        return (
          <Link
            key={href}
            href={href}
            className={cn(
              "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
              active
                ? "bg-[var(--primary)] text-[var(--primary-foreground)]"
                : "text-[var(--muted-foreground)] hover:bg-[var(--muted)] hover:text-[var(--foreground)]",
            )}
          >
            <Icon className="h-4 w-4 shrink-0" />
            {label}
          </Link>
        );
      })}
    </nav>
  );
}
