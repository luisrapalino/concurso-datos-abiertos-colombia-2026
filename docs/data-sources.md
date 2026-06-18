# Catálogo de fuentes de datos

Registro de proveniencia para ingestión y trazabilidad.

## datos-gov-mortality-indicators

| Campo | Valor |
|-------|--------|
| **ID interno** | `datos-gov-mortality-indicators` |
| **Nombre** | Indicadores de mortalidad y morbilidad (departamento / municipio / año) |
| **Proveedor** | Instituto Nacional de Salud (INS) vía [Datos Abiertos Colombia](https://www.datos.gov.co) |
| **Dataset** | [4e4i-ua65](https://www.datos.gov.co/Salud-y-Protecci-n-Social/Indicadores-mortalidad-y-morbilidad-seg-n-departam/4e4i-ua65) |
| **API** | Socrata Open Data API: `https://www.datos.gov.co/resource/4e4i-ua65.json` |
| **Licencia** | Datos abiertos Colombia (consultar condiciones del portal) |
| **Granularidad** | Municipal (código DANE 5 dígitos), serie anual |
| **Frecuencia de actualización** | Batch manual en MVP; worker Docker opcional cada 24 h |
| **Validación territorial** | Catálogo DANE DIVIPOLA embebido (`backend/data/divipola_municipality_catalog.json`) |
| **Indicador MVP** | `TASA DE MORTALIDAD GENERAL` → definición `general-mortality-rate` |
| **Unidad** | Tasa por 1 000 habitantes (según metadato del conjunto) |

### Linaje en base de datos

- Tabla `data_sources`: registro estático del catálogo.
- Tabla `ingestion_runs`: una fila por ejecución del CLI (`epintel-ingest`).
- Tabla `health_indicator_observations`: valores curados con FK a corrida de ingestión.

### Comando de ingestión

```bash
cd backend
export PYTHONPATH=src
export DATABASE_URL="postgresql+psycopg://epintel:epintel@localhost:5432/epintel"
python -m modules.epidemiological_surveillance.interfaces.cli ingest datos-gov-mortality-indicators
```

Opciones: `--year`, `--years`, `--limit`, `--dry-run`, `--skip-territorial-validation`.

Los registros con códigos municipales fuera de DIVIPOLA se descartan y se reportan como `records_rejected`.

### Actualizar catálogo DIVIPOLA

```bash
cd backend
python scripts/sync_divipola_catalog.py
```

### Ingestión programada (Docker)

El servicio `ingestion-worker` ejecuta ingestión multi-año cada 24 h (configurable vía `INGESTION_INTERVAL_HOURS`):

```bash
docker compose up -d ingestion-worker
```

Ejecución única:

```bash
docker compose run --rm ingestion-worker python -m modules.epidemiological_surveillance.interfaces.scheduler --once
```

---

## datos-gov-sivigila

| Campo | Valor |
|-------|--------|
| **ID interno** | `datos-gov-sivigila` |
| **Nombre** | Datos de Vigilancia en Salud Pública de Colombia (SIVIGILA) |
| **Dataset** | [4hyg-wa9d](https://www.datos.gov.co/resource/4hyg-wa9d.json) |
| **Granularidad** | Municipal, semana epidemiológica |
| **Indicador piloto** | Dengue (`cod_eve=210`) → `dengue-weekly-cases` |
| **Periodo interno** | `YYYY-Www` |

### Sincronización incremental por lotes (recomendado)

Descarga datos año a año, paginando de a 1000 registros. Para SIVIGILA prioriza las 18 ciudades principales.

```bash
# Todas las fuentes del reto, 2022 → 2018
./scripts/sync-open-data-batch.sh

# Una sola fuente
cd backend && export PYTHONPATH=src
python -m modules.epidemiological_surveillance.interfaces.cli ingest-sync datos-gov-sivigila-dengue \
  --batch-size 1000 --start-year 2022 --end-year 2018
```

Opciones: `--max-batches` (smoke test), `--all-municipalities`, `--territorial-codes 05001,11001`.

### Ingestión simple (legacy)

```bash
python -m modules.epidemiological_surveillance.interfaces.cli ingest datos-gov-sivigila-dengue --year 2020 --limit 20000
```

---

## datos-gov-vaccination-coverage

| Campo | Valor |
|-------|--------|
| **ID interno** | `datos-gov-vaccination-coverage` |
| **Dataset** | [6i25-2hdt](https://www.datos.gov.co/resource/6i25-2hdt.json) |
| **Granularidad** | Departamental (expandida a municipios vía DIVIPOLA) |
| **Indicador** | DPT-HepB-Hib pentavalente → `dpta-penta-vaccination-coverage` |

```bash
python -m modules.epidemiological_surveillance.interfaces.cli ingest datos-gov-vaccination-coverage --year 2020
```

---

## datos-gov-air-quality

| Campo | Valor |
|-------|--------|
| **ID interno** | `datos-gov-air-quality` |
| **Dataset** | [yspz-pxxn](https://www.datos.gov.co/resource/yspz-pxxn.json) |
| **Granularidad** | Estación diaria → PM2.5 anual municipal |
| **Indicador** | `pm25-annual-mean` |

```bash
python -m modules.epidemiological_surveillance.interfaces.cli ingest datos-gov-air-quality --year 2020
```

---

## Proxy de acceso a salud (misma fuente INS 4e4i-ua65)

| Indicador | Definición |
|-----------|------------|
| `PORCENTAJE DE PARTOS INSTITUCIONALES` | `institutional-births-coverage` |

```bash
python -m modules.epidemiological_surveillance.interfaces.cli ingest datos-gov-health-access --year 2020
```
