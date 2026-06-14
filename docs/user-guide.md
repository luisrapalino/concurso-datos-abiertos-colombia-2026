# Guía de usuario (MVP)

Plataforma de **Inteligencia Epidemiológica Territorial** — uso básico para revisión analítica.

## Acceso

| Servicio | URL local |
|----------|-----------|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000/docs |

Con Docker: `docker compose up --build` desde la raíz del repositorio.

## Flujo recomendado

1. Revisa la **frescura de datos** en el header (última ingestión INS / datos.gov.co).
2. Selecciona **código territorial** (5 dígitos DANE, ej. `05001`) y **periodo** (`YYYY-01`).
3. Recorre las vistas:
   - **Indicadores** — observaciones curadas.
   - **Mapa** — municipios DIVIPOLA con contornos departamentales DANE.
   - **Riesgo** — score explicable vs mediana nacional.
   - **Anomalías** — desviaciones respecto a la línea base del periodo.
   - **Tendencias** — histórico + proyección (Prophet o fallback lineal).
   - **Insights** — narrativa automática con contexto del sistema.

## Interpretación responsable

- El **riesgo territorial** prioriza revisión humana; no es alerta clínica ni decisión automática.
- La **cobertura** depende de lo publicado en datos abiertos; pueden existir lagunas territoriales.
- Las **proyecciones** son exploratorias; correlación histórica no implica causalidad.

## Datos de demo

- Territorio: `05001` (Medellín)
- Periodo con datos ingestados: `2020-01` (ajustar si ingestaste más años)

## Ingestión multi-año (operador)

```bash
cd backend
PYTHONPATH=src python -m modules.epidemiological_surveillance.interfaces.cli ingest \
  datos-gov-mortality-indicators --years 2018,2019,2020 --limit 15000
```

Más detalle operativo: [`runbook-release.md`](runbook-release.md) y [`demo-guide.md`](demo-guide.md).
