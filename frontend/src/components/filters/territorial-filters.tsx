"use client";

import { useEffect, useState } from "react";
import { CheckIcon, ChevronsUpDownIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import { Field, FieldGroup, FieldLabel } from "@/components/ui/field";
import { TRANSMISSIBLE_SIVIGILA_EVENTS, resolveEventLabel } from "@/lib/sivigila-events";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { epidemiologicalApi } from "@/lib/api/client";
import type { Municipality } from "@/lib/api/types";
import { FEATURED_MUNICIPALITIES } from "@/lib/featured-municipalities";
import { formatMunicipalityName } from "@/lib/domain-labels";
import { cn } from "@/lib/utils";
import { useTerritorialFilters } from "@/stores/territorial-filters";

export function TerritorialFilters() {
  const {
    territorialCode,
    municipalityName,
    eventCode,
    setMunicipality,
    setEpidemiologicalPeriod,
    setEventCode,
  } = useTerritorialFilters();
  const [municipalityOpen, setMunicipalityOpen] = useState(false);
  const [featured, setFeatured] = useState<Municipality[]>(
    FEATURED_MUNICIPALITIES.map(({ territorial_code, name, department_code, display_name }) => ({
      territorial_code,
      name,
      department_code,
      display_name,
    })),
  );

  useEffect(() => {
    epidemiologicalApi
      .getDataFreshness("datos-gov-sivigila")
      .then((freshness) => {
        if (freshness.latest_period_available?.includes("-W")) {
          setEpidemiologicalPeriod(freshness.latest_period_available);
        }
      })
      .catch(() => undefined);
  }, [setEpidemiologicalPeriod]);

  useEffect(() => {
    epidemiologicalApi
      .listFeaturedMunicipalities()
      .then(setFeatured)
      .catch(() => undefined);
  }, []);

  const handleSelectMunicipality = (item: Municipality) => {
    setMunicipality(item.territorial_code, item.name);
    setMunicipalityOpen(false);
  };

  const municipalityLabel = municipalityName
    ? formatMunicipalityName(municipalityName)
    : "Municipio…";

  return (
    <section
      aria-label="Filtros territoriales"
      className="liquid-glass-subtle print:hidden space-y-3 rounded-2xl p-4"
    >
      <FieldGroup className="gap-3 sm:grid sm:grid-cols-2 sm:items-end">
        <Field>
          <FieldLabel className="text-xs">Municipio</FieldLabel>
          <Popover open={municipalityOpen} onOpenChange={setMunicipalityOpen}>
            <PopoverTrigger
              render={
                <Button
                  variant="outline"
                  role="combobox"
                  aria-expanded={municipalityOpen}
                  className="h-8 w-full justify-between font-normal"
                />
              }
            >
              <span className="truncate">{municipalityLabel}</span>
              <ChevronsUpDownIcon className="size-3.5 shrink-0 opacity-50" />
            </PopoverTrigger>
            <PopoverContent className="w-(--anchor-width) p-0" align="start">
              <Command>
                <CommandInput placeholder="Nombre del municipio…" />
                <CommandList>
                  <CommandEmpty>Sin resultados</CommandEmpty>
                  <CommandGroup>
                    {featured.map((item) => (
                      <CommandItem
                        key={item.territorial_code}
                        value={formatMunicipalityName(item.name)}
                        onSelect={() => handleSelectMunicipality(item)}
                      >
                        <CheckIcon
                          className={cn(
                            "mr-2 size-3.5 shrink-0",
                            territorialCode === item.territorial_code
                              ? "opacity-100"
                              : "opacity-0",
                          )}
                        />
                        {formatMunicipalityName(item.name)}
                      </CommandItem>
                    ))}
                  </CommandGroup>
                </CommandList>
              </Command>
            </PopoverContent>
          </Popover>
        </Field>

        <Field>
          <FieldLabel className="text-xs">Enfermedad</FieldLabel>
          <Select
            value={eventCode}
            onValueChange={(value) => value && setEventCode(value)}
          >
            <SelectTrigger className="h-8 w-full">
              <SelectValue placeholder="Enfermedad">
                {resolveEventLabel(eventCode)}
              </SelectValue>
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                {TRANSMISSIBLE_SIVIGILA_EVENTS.map((event) => (
                  <SelectItem key={event.code} value={event.code}>
                    {event.name}
                  </SelectItem>
                ))}
              </SelectGroup>
            </SelectContent>
          </Select>
        </Field>
      </FieldGroup>
      <p className="text-xs text-muted-foreground">
        Contexto activo: {municipalityLabel} · {resolveEventLabel(eventCode)}
      </p>
    </section>
  );
}
