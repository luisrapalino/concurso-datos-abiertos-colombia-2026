# Matriz de criterios de aceptación

Criterios verificables del MVP institucional (`v0.3.0-mvp`). Cada fila enlaza una capacidad de negocio con evidencia reproducible.

| ID | Capacidad | Criterio de aceptación | Evidencia |
| --- | --- | --- | --- |
| A1 | Ingestión datos abiertos | Mortalidad general desde datos.gov.co persiste en PostgreSQL con trazabilidad de fuente | `POST` ingestión CLI/worker; `/api/v1/data-freshness` con `last_successful_ingestion_at` |
| A2 | Validación territorial | Códigos municipales inválidos se rechazan en ingestión cuando la validación está activa | `INGESTION_VALIDATE_TERRITORIAL_CODES=true`; catálogo DIVIPOLA embebido |
| A3 | Indicadores curados | Consulta por territorio y periodo devuelve observaciones tipadas | `/api/v1/health-indicators` |
| A4 | Riesgo explicable | Score 0–100 con clasificación, drivers y contribuciones de features | `/api/v1/predict-risk` |
| A5 | Anomalías | Listado paginado con severidad y valores observados vs baseline | `/api/v1/anomalies` |
| A6 | Tendencias | Serie histórica + proyección con supuestos explícitos | `/api/v1/territorial-trends` |
| A7 | Insights | Narrativa interpretable con fuentes y contexto de sistema | `/api/v1/insights` |
| A8 | Mapa territorial | Puntos DIVIPOLA + contornos departamentales GeoJSON | `/api/v1/territorial-risk-map`, `/territorial-boundaries` |
| A9 | Calidad y drift | Métricas de cobertura y estado stable/warning/alert entre periodos | `/data-quality`, `/data-drift` |
| A10 | ML promovible | Entrenamiento offline, promoción/rollback y SHAP en serving | `train_mortality_experiment.py`, `ml_cli`, evaluación temporal |
| A11 | Informe territorial | Reporte compuesto imprimible (riesgo + insights + drift) | `/api/v1/territorial-report`, UI `/informe` |
| A12 | Sesgo departamental | Resumen descriptivo de mortalidad por departamento | `/api/v1/bias-analysis` |
| A13 | Operación | Health, métricas, rate limit, backups verificables | `/health`, `/metrics`, scripts `backup-postgres.sh` |
| A14 | Seguridad opcional | API key en despliegues institucionales vía `X-API-Key` | `API_KEY` en entorno |
| A15 | Calidad automatizada | Pytest integración + smoke E2E Playwright | `pytest`, `npm run test:e2e` |

## Límites explícitos (no aceptación)

- No sustituye validación epidemiológica oficial ni decisiones clínicas.
- GeoJSON municipal completo y SIVIGILA quedan fuera del MVP (ver `post-mvp-roadmap.md`).
- OAuth2/SSO institucional es extensión post-MVP.

## Verificación rápida

```bash
docker compose up -d
cd backend && pytest -q
cd frontend && npm run test:e2e
./scripts/monitor-drift.sh
```
