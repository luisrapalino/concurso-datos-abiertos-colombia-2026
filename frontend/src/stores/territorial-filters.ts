import { create } from "zustand";
import { DEFAULT_FEATURED_MUNICIPALITY } from "@/lib/featured-municipalities";
import { DEFAULT_EVENT_CODE } from "@/lib/sivigila-events";

interface TerritorialFiltersState {
  territorialCode: string;
  municipalityName: string | null;
  period: string;
  epidemiologicalPeriod: string;
  eventCode: string;
  setMunicipality: (code: string, name: string | null) => void;
  setPeriod: (period: string) => void;
  setEpidemiologicalPeriod: (period: string) => void;
  setEventCode: (eventCode: string) => void;
}

export const useTerritorialFilters = create<TerritorialFiltersState>((set) => ({
  territorialCode: DEFAULT_FEATURED_MUNICIPALITY.territorial_code,
  municipalityName: DEFAULT_FEATURED_MUNICIPALITY.name,
  period: "2020-01",
  epidemiologicalPeriod: "2022-W01",
  eventCode: DEFAULT_EVENT_CODE,
  setMunicipality: (territorialCode, municipalityName) =>
    set({ territorialCode, municipalityName }),
  setPeriod: (period) => set({ period }),
  setEpidemiologicalPeriod: (epidemiologicalPeriod) => set({ epidemiologicalPeriod }),
  setEventCode: (eventCode) => set({ eventCode }),
}));
