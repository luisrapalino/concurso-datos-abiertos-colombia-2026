"use client";

import { MoonIcon, SunIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useTheme } from "@/hooks/use-theme";
import { cn } from "@/lib/utils";

type ThemeToggleProps = {
  className?: string;
  variant?: "floating" | "glass";
};

export function ThemeToggle({ className, variant = "floating" }: ThemeToggleProps) {
  const { resolved, toggle } = useTheme();

  return (
    <Button
      type="button"
      variant={variant === "glass" ? "ghost" : "outline"}
      size="icon"
      className={cn(
        variant === "floating" &&
          "fixed right-5 bottom-5 z-50 size-10 rounded-full border-border/70 bg-card/90 shadow-md backdrop-blur-sm hover:bg-accent hover:text-accent-foreground",
        variant === "glass" &&
          "size-8 shrink-0 rounded-full border-0 bg-transparent text-muted-foreground hover:bg-(--glass-nav-hover) hover:text-foreground",
        "print:hidden",
        className,
      )}
      onClick={toggle}
      aria-label={resolved === "dark" ? "Cambiar a modo claro" : "Cambiar a modo oscuro"}
    >
      {resolved === "dark" ? (
        <SunIcon className="size-4" />
      ) : (
        <MoonIcon className="size-4" />
      )}
    </Button>
  );
}
