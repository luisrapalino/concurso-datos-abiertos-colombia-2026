import { create } from "zustand";

interface TerritorialFiltersState {
  territorialCode: string;
  period: string;
  setTerritorialCode: (code: string) => void;
  setPeriod: (period: string) => void;
}

export const useTerritorialFilters = create<TerritorialFiltersState>((set) => ({
  territorialCode: "05001",
  period: "2020-01",
  setTerritorialCode: (territorialCode) => set({ territorialCode }),
  setPeriod: (period) => set({ period }),
}));
