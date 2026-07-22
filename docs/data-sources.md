# Catálogo de fuentes de datos

Registro de proveniencia para ingestión y trazabilidad.

Fuente de verdad del catálogo de bindings: [`backend/src/shared/municipal_dataset_catalog.py`](../backend/src/shared/municipal_dataset_catalog.py).  
Clientes Socrata (columnas `$select` / filtros): `backend/src/modules/epidemiological_surveillance/infrastructure/sources/`.

## Inventario de datasets y columnas

Se consumen **5 conjuntos** de [datos.gov.co](https://www.datos.gov.co) (4 fuentes lógicas; el quinto es fallback de calidad del aire). No se versionan dumps CSV en el repositorio: se leen por API SODA y se curan en PostgreSQL.

### Conjuntos utilizados

| #   | ID interno                         | Dataset (Socrata)                                               | Portal                                                                                                                                                       | Proveedor                       |
| --- | ---------------------------------- | --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------- |
| 1   | `datos-gov-mortality-indicators`   | [`4e4i-ua65`](https://www.datos.gov.co/resource/4e4i-ua65.json) | [Indicadores mortalidad/morbilidad](https://www.datos.gov.co/Salud-y-Protecci-n-Social/Indicadores-mortalidad-y-morbilidad-seg-n-departam/4e4i-ua65)         | INS                             |
| 2   | `datos-gov-sivigila`               | [`4hyg-wa9d`](https://www.datos.gov.co/resource/4hyg-wa9d.json) | [SIVIGILA](https://www.datos.gov.co/Salud-y-Protecci-n-Social/Datos-de-Vigilancia-en-Salud-P-blica-de-Colombia-SIVIGILA/4hyg-wa9d)                           | INS                             |
| 3   | `datos-gov-vaccination-coverage`   | [`6i25-2hdt`](https://www.datos.gov.co/resource/6i25-2hdt.json) | [Coberturas de vacunación](https://www.datos.gov.co/Salud-y-Protecci-n-Social/Coberturas-administrativas-de-vacunaci-n-por-departamento/6i25-2hdt)           | MinSalud                        |
| 4   | `datos-gov-air-quality` (primario) | [`kekd-7v7h`](https://www.datos.gov.co/resource/kekd-7v7h.json) | [Calidad del aire — promedio anual](https://www.datos.gov.co/Ambiente-y-Desarrollo-Sostenible/Calidad-del-Aire-en-Colombia-Promedio-Anual-/kekd-7v7h)        | IDEAM / autoridades ambientales |
| 5   | `datos-gov-air-quality` (fallback) | [`yspz-pxxn`](https://www.datos.gov.co/resource/yspz-pxxn.json) | [SISAIRE PM10/PM2.5](https://www.datos.gov.co/Ambiente-y-Desarrollo-Sostenible/Sistema-de-Informaci-n-sobre-Calidad-del-Aire-PM10-y-PM2-5-SISAIRE/yspz-pxxn) | IDEAM                           |

Datos de referencia embebidos (no son datasets del portal): `backend/data/divipola_municipality_catalog.json`, `backend/data/colombia_departments.geojson`.

### Variables de dominio (`definition_id`)

| Variable (UI)                     | `definition_id`                   | Dataset                   | Clave en origen                                      | Granularidad              |
| --------------------------------- | --------------------------------- | ------------------------- | ---------------------------------------------------- | ------------------------- |
| Tasa de mortalidad general        | `general-mortality-rate`          | `4e4i-ua65`               | `indicador` = `TASA DE MORTALIDAD GENERAL`           | Municipal anual           |
| Partos institucionales            | `institutional-births-coverage`   | `4e4i-ua65`               | `indicador` = `PORCENTAJE DE PARTOS INSTITUCIONALES` | Municipal anual           |
| Cobertura vacunal pentavalente    | `dpta-penta-vaccination-coverage` | `6i25-2hdt`               | `biol_gico` contiene `PENTA3`                        | Departamental → municipio |
| PM2.5 promedio anual              | `pm25-annual-mean`                | `kekd-7v7h` → `yspz-pxxn` | `variable` = `PM2.5` / columnas `pm25`·`pm10`        | Municipal anual           |
| Casos semanales — Dengue          | `dengue-weekly-cases`             | `4hyg-wa9d`               | `cod_eve` = `210`                                    | Municipal semanal         |
| Casos semanales — Chikungunya     | `chikungunya-weekly-cases`        | `4hyg-wa9d`               | `cod_eve` = `217`                                    | Municipal semanal         |
| Casos semanales — Dengue grave    | `dengue-severe-weekly-cases`      | `4hyg-wa9d`               | `cod_eve` = `220`                                    | Municipal semanal         |
| Casos semanales — Hepatitis A     | `hepatitis-a-weekly-cases`        | `4hyg-wa9d`               | `cod_eve` = `330`                                    | Municipal semanal         |
| Casos semanales — Hepatitis B     | `hepatitis-b-weekly-cases`        | `4hyg-wa9d`               | `cod_eve` = `340`                                    | Municipal semanal         |
| Casos semanales — Fiebre tifoidea | `typhoid-weekly-cases`            | `4hyg-wa9d`               | `cod_eve` = `320`                                    | Municipal semanal         |

Las features ML derivadas de estas observaciones están en [`data-dictionary.md`](data-dictionary.md).

### Columnas consumidas por dataset

Solo se solicitan las columnas necesarias (`$select`). El resto del esquema del portal no se usa.

#### `4e4i-ua65` — mortalidad / morbilidad

Cliente: `datos_gov_co_client.py` · `$select`: `codmunicipio,municipio,a_o,valor_indicador`

| Columna           | Uso                                                |
| ----------------- | -------------------------------------------------- |
| `indicador`       | Filtro (no va en `$select`): selecciona la métrica |
| `codmunicipio`    | Código DANE municipal                              |
| `municipio`       | Nombre territorial (metadato)                      |
| `a_o`             | Año calendario → periodo `YYYY-01`                 |
| `valor_indicador` | Valor numérico de la observación                   |

#### `4hyg-wa9d` — SIVIGILA

Cliente: `sivigila_client.py` · `$select`: `cod_mun_o,municipio_ocurrencia,ano,semana,conteo`

| Columna                | Uso                                        |
| ---------------------- | ------------------------------------------ |
| `cod_eve`              | Filtro: código de evento epidemiológico    |
| `cod_mun_o`            | Código DANE municipio de ocurrencia        |
| `municipio_ocurrencia` | Nombre territorial (metadato)              |
| `ano`                  | Año calendario                             |
| `semana`               | Semana epidemiológica → periodo `YYYY-Www` |
| `conteo`               | Casos agregados                            |

#### `6i25-2hdt` — vacunación

Cliente: `vaccination_client.py` · `$select`: `coddepto,departamento,biol_gico,a_o,cobertura_de_vacunaci_n`

| Columna                   | Uso                                                         |
| ------------------------- | ----------------------------------------------------------- |
| `coddepto`                | Código departamental (se expande a municipios vía DIVIPOLA) |
| `departamento`            | Nombre (metadato)                                           |
| `biol_gico`               | Filtro en cliente: biológicos con `PENTA3`                  |
| `a_o`                     | Año calendario → periodo `YYYY-01`                          |
| `cobertura_de_vacunaci_n` | Cobertura (%)                                               |

#### `kekd-7v7h` — calidad del aire (promedio anual)

Cliente: `air_quality_client.py` · `$select`: `a_o,promedio,nombre_del_municipio,id_estacion`

| Columna                      | Uso                                               |
| ---------------------------- | ------------------------------------------------- |
| `c_digo_del_municipio`       | Filtro `$where` (código numérico abierto)         |
| `variable`                   | Filtro `$where` = `PM2.5`                         |
| `tiempo_de_exposici_n_horas` | Filtro `$where` = `24`                            |
| `a_o`                        | Año → periodo anual                               |
| `promedio`                   | Concentración; se agrega por municipio/año        |
| `nombre_del_municipio`       | Nombre (metadato)                                 |
| `id_estacion`                | Identificador de estación (trazabilidad de filas) |

#### `yspz-pxxn` — SISAIRE (fallback PM2.5)

Cliente: `sisaire_air_quality_client.py` · `$select`: `fecha_lectura,pm25,pm10,estacion`

| Columna         | Uso                                                  |
| --------------- | ---------------------------------------------------- |
| `estacion`      | Filtro `$where` por nombre de municipio              |
| `fecha_lectura` | Fecha → año calendario                               |
| `pm25`          | Valor preferido                                      |
| `pm10`          | Respaldo si `pm25` está vacío; media anual municipal |

---

## Modos de ingesta

| Modo                        | Comando                           | Uso                                                            |
| --------------------------- | --------------------------------- | -------------------------------------------------------------- |
| **Municipal (recomendado)** | `ingest-sync-municipal`           | Resuelve el mejor dataset por variable; fallback PM2.5 SISAIRE |
| Sync por fuente             | `ingest-sync` / `ingest-sync-all` | Paginación año × municipio por fuente                          |
| Batch legacy                | `ingest`                          | Solo smoke tests; puede truncar con `--limit`                  |

El worker Docker (`ingestion-worker`) ejecuta **`ingest-sync-municipal`** cada **24 h** (`INGESTION_INTERVAL_HOURS`) sobre los **20 municipios destacados** definidos en [`featured_municipalities.py`](../backend/src/shared/featured_municipalities.py) (`FEATURED_MUNICIPALITIES` = `EXPANDED_MUNICIPALITIES`: 4 piloto + 16 capitales adicionales). Sin `--territorial-codes`, el scheduler usa ese catálogo por defecto.

| Alcance                  | Códigos                                                                   | Uso                                                                                          |
| ------------------------ | ------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| **Destacados (default)** | 20 municipios                                                             | Worker, API `featured_only`, `./scripts/sync-open-data-batch.sh` / `sync-expanded-cities.sh` |
| **Piloto**               | Medellín, Bogotá, Barranquilla, Cali (`05001`, `11001`, `08001`, `76001`) | Subconjunto histórico; `./scripts/sync-pilot-cities.sh`                                      |

### Token Socrata (recomendado)

Registra un App Token en [datos.gov.co → Developer Settings](https://www.datos.gov.co/profile/edit/developer_settings) y configúralo como `SOCRATA_APP_TOKEN`. Mejora los límites de tasa y evita throttling por IP compartida ([documentación Socrata](https://dev.socrata.com/docs/app-tokens.html)).

### Trazabilidad en base de datos

- Tabla `data_sources`: catálogo estático de fuentes.
- Tabla `ingestion_runs`: una fila por corrida con metadatos (`sync_mode`, `records_rejected`, `batches_processed`, `years_processed`, `territorial_codes`, `bindings_used`).
- Tabla `health_indicator_observations`: valores curados con FK a corrida de ingestión.

---

## datos-gov-mortality-indicators

| Campo                           | Valor                                                                                                                        |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| **ID interno**                  | `datos-gov-mortality-indicators`                                                                                             |
| **Nombre**                      | Indicadores de mortalidad y morbilidad (departamento / municipio / año)                                                      |
| **Proveedor**                   | Instituto Nacional de Salud (INS) vía [Datos Abiertos Colombia](https://www.datos.gov.co)                                    |
| **Dataset**                     | [4e4i-ua65](https://www.datos.gov.co/Salud-y-Protecci-n-Social/Indicadores-mortalidad-y-morbilidad-seg-n-departam/4e4i-ua65) |
| **API**                         | Socrata: `https://www.datos.gov.co/resource/4e4i-ua65.json`                                                                  |
| **Licencia**                    | Datos abiertos Colombia (consultar condiciones del portal)                                                                   |
| **Granularidad**                | Municipal (código DANE 5 dígitos), serie anual                                                                               |
| **Frecuencia de actualización** | Worker Docker cada 24 h (configurable vía `INGESTION_INTERVAL_HOURS`)                                                        |
| **Validación territorial**      | Catálogo DANE DIVIPOLA embebido (`backend/data/divipola_municipality_catalog.json`)                                          |
| **Indicador MVP**               | `TASA DE MORTALIDAD GENERAL` → definición `general-mortality-rate`                                                           |
| **También usa**                 | `PORCENTAJE DE PARTOS INSTITUCIONALES` → `institutional-births-coverage`                                                     |
| **Unidad**                      | Tasa por 1 000 habitantes (según metadato del conjunto)                                                                      |
| **Columnas**                    | `$select`: `codmunicipio,municipio,a_o,valor_indicador`; filtro `indicador` (ver inventario)                                 |

```bash
cd backend
export PYTHONPATH=src
export DATABASE_URL="postgresql+psycopg://epintel:epintel@localhost:5432/epintel"
# Sin --territorial-codes: usa los 20 municipios destacados (FEATURED_MUNICIPALITY_CODES)
python -m modules.epidemiological_surveillance.interfaces.cli ingest-sync-municipal \
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

| Campo               | Valor                                                                                            |
| ------------------- | ------------------------------------------------------------------------------------------------ |
| **ID interno**      | `datos-gov-sivigila`                                                                             |
| **Nombre**          | Datos de Vigilancia en Salud Pública de Colombia (SIVIGILA)                                      |
| **Dataset**         | [4hyg-wa9d](https://www.datos.gov.co/resource/4hyg-wa9d.json)                                    |
| **Granularidad**    | Municipal, semana epidemiológica                                                                 |
| **Indicadores**     | Dengue, chikungunya, dengue grave, hepatitis A/B, fiebre tifoidea                                |
| **Periodo interno** | `YYYY-Www`                                                                                       |
| **Columnas**        | `$select`: `cod_mun_o,municipio_ocurrencia,ano,semana,conteo`; filtro `cod_eve` (ver inventario) |

### Sincronización incremental por lotes (recomendado)

Descarga datos año a año, paginando de a 1000 registros, filtrando por los **20 municipios destacados** (default del catálogo).

```bash
# Ampliado: 20 ciudades principales (FEATURED_MUNICIPALITIES)
./scripts/sync-open-data-batch.sh

# Solo 4 piloto (opcional)
./scripts/sync-pilot-cities.sh

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

| Campo            | Valor                                                                                     |
| ---------------- | ----------------------------------------------------------------------------------------- |
| **ID interno**   | `datos-gov-vaccination-coverage`                                                          |
| **Dataset**      | [6i25-2hdt](https://www.datos.gov.co/resource/6i25-2hdt.json)                             |
| **Granularidad** | Departamental (expandida al municipio solicitado vía DIVIPOLA)                            |
| **Indicador**    | DPT-HepB-Hib pentavalente → `dpta-penta-vaccination-coverage`                             |
| **Columnas**     | `$select`: `coddepto,departamento,biol_gico,a_o,cobertura_de_vacunaci_n` (ver inventario) |

```bash
python -m modules.epidemiological_surveillance.interfaces.cli ingest-sync-municipal \
  --definition-ids dpta-penta-vaccination-coverage --start-year 2022 --end-year 2018
```

---

## datos-gov-air-quality

| Campo                   | Valor                                                                                                                                  |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| **ID interno**          | `datos-gov-air-quality`                                                                                                                |
| **Dataset primario**    | [kekd-7v7h](https://www.datos.gov.co/resource/kekd-7v7h.json) — PM2.5 promedio anual municipal                                         |
| **Dataset fallback**    | [yspz-pxxn](https://www.datos.gov.co/resource/yspz-pxxn.json) — SISAIRE lecturas diarias                                               |
| **Granularidad**        | Estación → agregación anual municipal                                                                                                  |
| **Indicador**           | `pm25-annual-mean`                                                                                                                     |
| **Columnas (primario)** | `$select`: `a_o,promedio,nombre_del_municipio,id_estacion`; `$where`: `c_digo_del_municipio`, `variable`, `tiempo_de_exposici_n_horas` |
| **Columnas (fallback)** | `$select`: `fecha_lectura,pm25,pm10,estacion` (ver inventario)                                                                         |

El resolver municipal intenta primero `kekd-7v7h` y, si no hay datos, usa `yspz-pxxn` (SISAIRE).

```bash
python -m modules.epidemiological_surveillance.interfaces.cli ingest-sync-municipal \
  --definition-ids pm25-annual-mean --start-year 2022 --end-year 2018
```

---

## Proxy de acceso a salud (misma fuente INS 4e4i-ua65)

| Indicador                              | Definición                      |
| -------------------------------------- | ------------------------------- |
| `PORCENTAJE DE PARTOS INSTITUCIONALES` | `institutional-births-coverage` |

```bash
python -m modules.epidemiological_surveillance.interfaces.cli ingest-sync-municipal \
  --definition-ids institutional-births-coverage --start-year 2022 --end-year 2018
```
