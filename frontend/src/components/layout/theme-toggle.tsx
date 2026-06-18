"use client";

import { MoonIcon, SunIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useTheme } from "@/hooks/use-theme";

export function ThemeToggle() {
  const { resolved, toggle } = useTheme();

  return (
    <Button
      type="button"
      variant="ghost"
      size="icon-sm"
      className="ml-auto shrink-0 print:hidden"
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
