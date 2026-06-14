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
| **Frecuencia de actualización** | Según publicación en portal (batch manual en MVP) |
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

Opciones: `--year`, `--limit`, `--dry-run`.
