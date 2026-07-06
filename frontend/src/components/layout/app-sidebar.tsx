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
  { href: "/radar", label: "Radar", icon: Home },
  { href: "/brotes", label: "Ficha", icon: Bug },
  { href: "/mapa", label: "Mapa", icon: Map },
  { href: "/informe", label: "Informe", icon: FileText },
  { href: "/datos", label: "Datos", icon: Database },
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
      <SidebarHeader className="shrink-0 border-b border-sidebar-border px-2 py-3 group-data-[collapsible=icon]:border-b-0">
        <div className="flex min-w-0 items-center">
          <div className="flex size-10 shrink-0 items-center justify-center">
            <div className="flex size-9 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground shadow-sm">
              <Bug className="size-4" />
            </div>
          </div>
          <div
            className={cn(
              "min-w-0 overflow-hidden pl-1 transition-[opacity,width] duration-200 ease-linear",
              isCollapsed ? "w-0 opacity-0" : "flex-1 opacity-100",
            )}
          >
            <p className="truncate font-heading text-sm font-semibold leading-snug text-sidebar-foreground">
              Radar de brotes
            </p>
            <p className="truncate text-xs leading-snug text-sidebar-foreground/60">
              Inteligencia territorial
            </p>
          </div>
        </div>
      </SidebarHeader>

      <SidebarContent className="px-2 pt-3">
        <SidebarGroup className="px-0 py-0">
          <SidebarGroupContent>
            <SidebarMenu className="gap-1.5">
              {navItems.map(({ href, label, icon: Icon }) => {
                const isActive = pathname === href;
                return (
                  <SidebarMenuItem key={href}>
                    <SidebarMenuButton
                      render={<Link href={href} />}
                      isActive={isActive}
                      tooltip={isCollapsed ? label : undefined}
                      className={cn(
                        "h-10 w-full gap-0 rounded-lg px-0",
                        "group-data-[collapsible=icon]:size-auto! group-data-[collapsible=icon]:h-10! group-data-[collapsible=icon]:w-full! group-data-[collapsible=icon]:p-0!",
                        "data-active:bg-sidebar-primary data-active:text-sidebar-primary-foreground",
                      )}
                    >
                      <span className="flex size-10 shrink-0 items-center justify-center">
                        <Icon className="size-4.5" />
                      </span>
                      <span
                        className={cn(
                          "min-w-0 truncate text-sm font-medium transition-[opacity,width] duration-200 ease-linear",
                          isCollapsed ? "w-0 opacity-0" : "flex-1 pr-2 opacity-100",
                        )}
                      >
                        {label}
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
