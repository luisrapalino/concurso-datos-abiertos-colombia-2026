import type { Metadata } from "next";
import { RootShell } from "@/components/layout/root-shell";
import { ThemeScript } from "@/components/layout/theme-script";
import { TooltipProvider } from "@/components/ui/tooltip";
import "./fonts.css";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "Radar de Brotes — Inteligencia epidemiológica territorial",
    template: "%s · Radar de Brotes",
  },
  description:
    "Predicción explicable de brotes con datos abiertos de Colombia. Random Forest, SHAP y vigilancia territorial.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es" className="h-full antialiased" suppressHydrationWarning>
      <head>
        <ThemeScript />
      </head>
      <body className="min-h-full">
        <TooltipProvider>
          <RootShell>{children}</RootShell>
        </TooltipProvider>
      </body>
    </html>
  );
}
