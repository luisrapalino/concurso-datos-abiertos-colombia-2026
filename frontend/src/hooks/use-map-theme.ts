"use client";

import {
  classificationColors,
  classificationColorsDark,
  mapThemeDark,
  mapThemeLight,
} from "@/components/map/colombia-map-theme";
import { useIsDark } from "@/hooks/use-is-dark";

export function useMapTheme() {
  const isDark = useIsDark();
  return {
    theme: isDark ? mapThemeDark : mapThemeLight,
    classificationColors: isDark ? classificationColorsDark : classificationColors,
  };
}
