"use client";

import { usePathname } from "next/navigation";
import { AppShell } from "@/components/layout/app-shell";

const MARKETING_PATHS = new Set(["/"]);

export function RootShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  if (MARKETING_PATHS.has(pathname)) {
    return <>{children}</>;
  }

  return <AppShell>{children}</AppShell>;
}
