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
- Modelos ML:
  ```bash
  cd backend
  PYTHONPATH=src python -m modules.territorial_risk.interfaces.ml_cli rollback
  ```
  Sin versión promovida, serving vuelve a `mortality-relative-v1.0.0` (rule-based).

## Etiquetado

```bash
git tag -a v0.1.1-mvp -m "MVP + DIVIPOLA + SHAP serving + backups"
git push origin v0.1.1-mvp
```

Operación diaria: [`runbook-operations.md`](runbook-operations.md).
