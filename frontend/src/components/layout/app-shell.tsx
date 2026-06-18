"use client";

import { AppSidebar } from "@/components/layout/app-sidebar";
import { ThemeToggle } from "@/components/layout/theme-toggle";
import { PageTransition } from "@/components/motion/page-transition";
import { TerritorialFilters } from "@/components/filters/territorial-filters";
import {
  SidebarInset,
  SidebarProvider,
} from "@/components/ui/sidebar";
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
    <SidebarProvider
      defaultOpen={false}
      style={{ "--sidebar-width-icon": "3.25rem" } as React.CSSProperties}
    >
      <AppSidebar />
      <SidebarInset className="topography-surface">
        <ThemeToggle />

        <div className="flex flex-1 flex-col px-5 py-6 md:px-8 md:py-8 print:p-0">
          <ContentColumn>
            <TerritorialFilters />
            <main className="flex-1">
              <PageTransition>{children}</PageTransition>
            </main>
            <footer className="app-chrome border-t border-border/40 pt-4 text-xs text-muted-foreground">
              <p>Apoyo a priorización territorial · datos abiertos Colombia</p>
            </footer>
          </ContentColumn>
        </div>
      </SidebarInset>
    </SidebarProvider>
  );
}
