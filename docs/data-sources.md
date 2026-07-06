# Catálogo de fuentes de datos

Registro de proveniencia para ingestión y trazabilidad.

## Modos de ingesta

| Modo | Comando | Uso |
|------|---------|-----|
| **Municipal (recomendado)** | `ingest-sync-municipal` | Resuelve el mejor dataset por variable; fallback PM2.5 SISAIRE |
| Sync por fuente | `ingest-sync` / `ingest-sync-all` | Paginación año × municipio por fuente |
| Batch legacy | `ingest` | Solo smoke tests; puede truncar con `--limit` |

El worker Docker (`ingestion-worker`) ejecuta **`ingest-sync-municipal`** cada 24 h sobre las **4 ciudades piloto** (Medellín, Bogotá, Barranquilla, Cali).

### Token Socrata (recomendado)

Registra un App Token en [datos.gov.co → Developer Settings](https://www.datos.gov.co/profile/edit/developer_settings) y configúralo como `SOCRATA_APP_TOKEN`. Mejora los límites de tasa y evita throttling por IP compartida ([documentación Socrata](https://dev.socrata.com/docs/app-tokens.html)).

### Trazabilidad en base de datos

- Tabla `data_sources`: catálogo estático de fuentes.
- Tabla `ingestion_runs`: una fila por corrida con metadatos (`sync_mode`, `records_rejected`, `batches_processed`, `years_processed`, `territorial_codes`, `bindings_used`).
- Tabla `health_indicator_observations`: valores curados con FK a corrida de ingestión.

---

## datos-gov-mortality-indicators

| Campo | Valor |
|-------|--------|
| **ID interno** | `datos-gov-mortality-indicators` |
| **Nombre** | Indicadores de mortalidad y morbilidad (departamento / municipio / año) |
| **Proveedor** | Instituto Nacional de Salud (INS) vía [Datos Abiertos Colombia](https://www.datos.gov.co) |
| **Dataset** | [4e4i-ua65](https://www.datos.gov.co/Salud-y-Protecci-n-Social/Indicadores-mortalidad-y-morbilidad-seg-n-departam/4e4i-ua65) |
| **API** | Socrata: `https://www.datos.gov.co/resource/4e4i-ua65.json` |
| **Licencia** | Datos abiertos Colombia (consultar condiciones del portal) |
| **Granularidad** | Municipal (código DANE 5 dígitos), serie anual |
| **Frecuencia de actualización** | Worker Docker cada 24 h (configurable vía `INGESTION_INTERVAL_HOURS`) |
| **Validación territorial** | Catálogo DANE DIVIPOLA embebido (`backend/data/divipola_municipality_catalog.json`) |
| **Indicador MVP** | `TASA DE MORTALIDAD GENERAL` → definición `general-mortality-rate` |
| **Unidad** | Tasa por 1 000 habitantes (según metadato del conjunto) |

```bash
cd backend
export PYTHONPATH=src
export DATABASE_URL="postgresql+psycopg://epintel:epintel@localhost:5432/epintel"
python -m modules.epidemiological_surveillance.interfaces.cli ingest-sync-municipal \
  --territorial-codes 05001,11001,08001,76001 \
  --start-year 2022 --end-year 2018
```

Opciones: `--year`, `--years`, `--limit`, `--dry-run`, `--skip-territorial-validation` (solo modo legacy `ingest`).

Los registros con códigos municipales fuera de DIVIPOLA se descartan y se reportan como `records_rejected`.

### Actualizar catálogo DIVIPOLA

```bash
cd backend
python scripts/sync_divipola_catalog.py
```

### Ingestión programada (Docker)

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
| **Indicadores** | Dengue, chikungunya, dengue grave, hepatitis A/B, fiebre tifoidea |
| **Periodo interno** | `YYYY-Www` |

### Sincronización incremental por lotes (recomendado)

Descarga datos año a año, paginando de a 1000 registros, filtrando por municipio piloto.

```bash
# Piloto: 4 ciudades (Medellín, Bogotá, Barranquilla, Cali)
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
| **Granularidad** | Departamental (expandida al municipio solicitado vía DIVIPOLA) |
| **Indicador** | DPT-HepB-Hib pentavalente → `dpta-penta-vaccination-coverage` |

```bash
python -m modules.epidemiological_surveillance.interfaces.cli ingest-sync-municipal \
  --definition-ids dpta-penta-vaccination-coverage --start-year 2022 --end-year 2018
```

---

## datos-gov-air-quality

| Campo | Valor |
|-------|--------|
| **ID interno** | `datos-gov-air-quality` |
| **Dataset primario** | [kekd-7v7h](https://www.datos.gov.co/resource/kekd-7v7h.json) — PM2.5 promedio anual municipal |
| **Dataset fallback** | [yspz-pxxn](https://www.datos.gov.co/resource/yspz-pxxn.json) — SISAIRE lecturas diarias |
| **Granularidad** | Estación → agregación anual municipal |
| **Indicador** | `pm25-annual-mean` |

El resolver municipal intenta primero `kekd-7v7h` y, si no hay datos, usa `yspz-pxxn` (SISAIRE).

```bash
python -m modules.epidemiological_surveillance.interfaces.cli ingest-sync-municipal \
  --definition-ids pm25-annual-mean --start-year 2022 --end-year 2018
```

---

## Proxy de acceso a salud (misma fuente INS 4e4i-ua65)

| Indicador | Definición |
|-----------|------------|
| `PORCENTAJE DE PARTOS INSTITUCIONALES` | `institutional-births-coverage` |

```bash
python -m modules.epidemiological_surveillance.interfaces.cli ingest-sync-municipal \
  --definition-ids institutional-births-coverage --start-year 2022 --end-year 2018
```
