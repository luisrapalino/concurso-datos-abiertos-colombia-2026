"use client";

import { MoonIcon, SunIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useTheme } from "@/hooks/use-theme";
import { cn } from "@/lib/utils";

export function ThemeToggle({ className }: { className?: string }) {
  const { resolved, toggle } = useTheme();

  return (
    <Button
      type="button"
      variant="outline"
      size="icon"
      className={cn(
        "fixed right-5 bottom-5 z-50 size-10 rounded-full border-border/70 bg-card/90 shadow-md backdrop-blur-sm print:hidden",
        "hover:bg-accent hover:text-accent-foreground",
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
