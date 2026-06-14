# Guía de release (MVP institucional)

Checklist para la fase 10 del roadmap.

## Pre-release

- [ ] `docker compose up --build` levanta `db`, `api` y `web`.
- [ ] Migraciones Alembic aplicables desde cero (`alembic upgrade head`).
- [ ] Tests backend (`pytest`) y frontend (`npm run lint && npm run build`) en verde.
- [ ] Ingestión de referencia ejecutada para el periodo demo (`2020-01`).
- [ ] OpenAPI publicado en `/docs` y alineado con tipos del frontend.

## Demo institucional sugerida

1. Mostrar **frescura de datos** en el header (fuente INS / datos.gov.co).
2. Filtrar territorio `05001`, periodo `2020-01`.
3. Recorrer indicadores → riesgo (contribuciones) → anomalías → tendencias → insights.
4. Abrir **mapa territorial** con clasificación por score.
5. Enfatizar límites: no decisión clínica automática, cobertura parcial.

## Rollback

- API: revertir imagen Docker anterior y mantener migraciones compatibles hacia adelante.
- Modelos: serving rule-based permanece canónico; experimentos ML viven en `backend/ml/artifacts/`.

## Etiquetado

```bash
git tag -a v0.1.0-mvp -m "MVP institucional territorial"
git push origin v0.1.0-mvp
```
