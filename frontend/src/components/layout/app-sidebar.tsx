"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Bug, Database, FileText, Home, Map } from "lucide-react";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/", label: "Radar", description: "Ranking territorial", icon: Home },
  { href: "/brotes", label: "Ficha", description: "Señal y factores", icon: Bug },
  { href: "/mapa", label: "Mapa", description: "Vista geográfica", icon: Map },
  { href: "/informe", label: "Informe", description: "Resumen exportable", icon: FileText },
  { href: "/datos", label: "Datos", description: "Fuentes abiertas", icon: Database },
];

export function AppSidebar() {
  const pathname = usePathname();
  const { setHoverOpen, isMobile, state } = useSidebar();
  const isCollapsed = state === "collapsed";

  return (
    <Sidebar
      collapsible="icon"
      variant="floating"
      onMouseEnter={() => {
        if (!isMobile) setHoverOpen(true);
      }}
      onMouseLeave={() => {
        if (!isMobile) setHoverOpen(false);
      }}
    >
      <SidebarHeader className="shrink-0 border-b border-sidebar-border px-4 py-5 group-data-[collapsible=icon]:border-b-0 group-data-[collapsible=icon]:px-0 group-data-[collapsible=icon]:py-3">
        <div className="flex w-full items-center gap-3 group-data-[collapsible=icon]:justify-center">
          <div className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground shadow-sm group-data-[collapsible=icon]:size-8">
            <Bug className="size-4" />
          </div>
          <div className="min-w-0 space-y-0.5 group-data-[collapsible=icon]:hidden">
            <p className="truncate font-heading text-sm font-semibold leading-snug text-sidebar-foreground">
              Radar de brotes
            </p>
            <p className="truncate text-xs leading-snug text-sidebar-foreground/60">
              Inteligencia territorial
            </p>
          </div>
        </div>
      </SidebarHeader>

      <SidebarContent className="px-1 pt-3 group-data-[collapsible=icon]:px-0 group-data-[collapsible=icon]:pt-2">
        <SidebarGroup className="px-3 py-0 group-data-[collapsible=icon]:px-0">
          <SidebarGroupContent className="group-data-[collapsible=icon]:flex group-data-[collapsible=icon]:flex-col group-data-[collapsible=icon]:items-center">
            <SidebarMenu className="gap-1.5 group-data-[collapsible=icon]:w-full group-data-[collapsible=icon]:items-center group-data-[collapsible=icon]:gap-2">
              {navItems.map(({ href, label, description, icon: Icon }) => {
                const isActive = pathname === href;
                return (
                  <SidebarMenuItem
                    key={href}
                    className="group-data-[collapsible=icon]:flex group-data-[collapsible=icon]:w-full group-data-[collapsible=icon]:justify-center"
                  >
                    <SidebarMenuButton
                      render={<Link href={href} />}
                      isActive={isActive}
                      tooltip={isCollapsed ? label : undefined}
                      className={cn(
                        "h-auto min-h-12 gap-3 rounded-lg px-3 py-2.5",
                        "data-active:bg-sidebar-primary data-active:text-sidebar-primary-foreground",
                        "group-data-[collapsible=icon]:!size-10 group-data-[collapsible=icon]:!min-h-0",
                        "group-data-[collapsible=icon]:justify-center group-data-[collapsible=icon]:!p-0",
                      )}
                    >
                      <Icon className="size-[1.125rem] shrink-0" />
                      <span className="flex min-w-0 flex-col items-start gap-0.5 leading-none group-data-[collapsible=icon]:hidden">
                        <span className="text-sm font-medium leading-snug">{label}</span>
                        <span
                          className={cn(
                            "text-[11px] font-normal leading-snug",
                            isActive
                              ? "text-sidebar-primary-foreground/80"
                              : "text-sidebar-foreground/55",
                          )}
                        >
                          {description}
                        </span>
                      </span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
}
