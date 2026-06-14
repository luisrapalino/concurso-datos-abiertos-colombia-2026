"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useTerritorialFilters } from "@/stores/territorial-filters";

export function TerritorialFilters() {
  const { territorialCode, period, setTerritorialCode, setPeriod } =
    useTerritorialFilters();
  const [draftCode, setDraftCode] = useState(territorialCode);
  const [draftPeriod, setDraftPeriod] = useState(period);

  function applyFilters(event: React.FormEvent) {
    event.preventDefault();
    setTerritorialCode(draftCode.trim());
    setPeriod(draftPeriod.trim());
  }

  return (
    <form
      onSubmit={applyFilters}
      className="flex flex-col gap-3 rounded-lg border border-[var(--border)] bg-[var(--muted)]/40 p-3 sm:flex-row sm:items-end"
    >
      <div className="grid w-full gap-1.5 sm:w-40">
        <Label htmlFor="territorial-code">Código territorial</Label>
        <Input
          id="territorial-code"
          inputMode="numeric"
          pattern="[0-9]{5}"
          maxLength={5}
          placeholder="05001"
          value={draftCode}
          onChange={(event) => setDraftCode(event.target.value)}
        />
      </div>
      <div className="grid w-full gap-1.5 sm:w-36">
        <Label htmlFor="period">Periodo</Label>
        <Input
          id="period"
          placeholder="2020-01"
          pattern="[0-9]{4}-[0-9]{2}"
          value={draftPeriod}
          onChange={(event) => setDraftPeriod(event.target.value)}
        />
      </div>
      <Button type="submit" className="sm:w-auto">
        Aplicar
      </Button>
    </form>
  );
}
