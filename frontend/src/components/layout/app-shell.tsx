"use client";

import { AppTopNav, FLOATING_NAV_OFFSET } from "@/components/layout/app-top-nav";
import { PageTransition } from "@/components/motion/page-transition";
import { TerritorialFilters } from "@/components/filters/territorial-filters";
import { cn } from "@/lib/utils";

function ContentColumn({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "mx-auto flex w-full max-w-6xl flex-col gap-7 md:gap-8",
        className,
      )}
    >
      {children}
    </div>
  );
}

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="topography-surface min-h-screen">
      <AppTopNav />

      <div className={cn("flex flex-1 flex-col px-5 pb-6 md:px-8 md:pb-8 print:p-0", FLOATING_NAV_OFFSET)}>
        <ContentColumn>
          <TerritorialFilters />
          <main className="flex-1">
            <PageTransition>{children}</PageTransition>
          </main>
          <footer className="app-chrome border-t border-border/30 pt-4 text-xs text-muted-foreground">
            <p>Apoyo a priorización territorial · datos abiertos Colombia</p>
          </footer>
        </ContentColumn>
      </div>
    </div>
  );
}
