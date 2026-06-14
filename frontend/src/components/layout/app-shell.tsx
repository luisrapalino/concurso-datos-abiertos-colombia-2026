"use client";

import { TerritorialFilters } from "@/components/filters/territorial-filters";
import { NavBar } from "@/components/layout/nav-bar";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-[var(--background)]">
      <header className="border-b border-[var(--border)] bg-[var(--card)]">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-[var(--primary)]">
                Datos abiertos · Colombia
              </p>
              <h1 className="text-xl font-bold text-[var(--foreground)]">
                Inteligencia Epidemiológica Territorial
              </h1>
              <p className="text-sm text-[var(--muted-foreground)]">
                Análisis explicable de indicadores, riesgo, anomalías y tendencias.
              </p>
            </div>
            <TerritorialFilters />
          </div>
        </div>
      </header>

      <div className="mx-auto flex max-w-7xl flex-col gap-6 px-4 py-6 sm:px-6 lg:flex-row lg:px-8">
        <aside className="lg:w-56 lg:shrink-0">
          <div className="sticky top-6 rounded-lg border border-[var(--border)] bg-[var(--card)] p-3">
            <NavBar />
          </div>
        </aside>
        <main className="min-w-0 flex-1">{children}</main>
      </div>
    </div>
  );
}
