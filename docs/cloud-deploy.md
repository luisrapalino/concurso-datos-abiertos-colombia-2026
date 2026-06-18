# Despliegue en nube

Guía mínima para desplegar la plataforma en un entorno institucional (VM o contenedor gestionado).

## Componentes

| Servicio | Imagen / build | Puerto |
| --- | --- | --- |
| API | `backend/Dockerfile` | 8000 |
| Web | `frontend/Dockerfile` | 3000 |
| PostgreSQL | `postgres:16-alpine` | 5432 |
| Worker ingestión | mismo backend | — |

## Variables de entorno críticas

```bash
DATABASE_URL=postgresql+psycopg://USER:PASS@postgres:5432/epintel
CORS_ORIGINS=https://epintel.ejemplo.gov.co
NEXT_PUBLIC_API_URL=https://api.epintel.ejemplo.gov.co
API_INTERNAL_URL=http://api:8000
API_KEY=<clave-larga-aleatoria>          # opcional; protege /api/v1/*
ML_ARTIFACTS_DIR=/var/lib/epintel/ml
GEOJSON_DATA_DIR=/var/lib/epintel/geojson
INGESTION_SCHEDULE_ENABLED=true
INGESTION_INTERVAL_HOURS=24
```

No incluyas secretos en imágenes Docker; usa un gestor (AWS SSM, GCP Secret Manager, Vault, etc.).

## Pasos recomendados

1. **Base de datos:** Postgres gestionado o contenedor con volumen persistente.
2. **Migraciones:** ejecutar Alembic antes de levantar tráfico (`alembic upgrade head`).
3. **Datos iniciales:** ingestión CLI o worker (`ingestion-worker` en Compose).
4. **Artefactos ML:** montar volumen con modelos promovidos o entrenar en CI offline.
5. **Reverse proxy:** TLS terminado en nginx/Traefik; reenviar `/api/v1` al backend.
6. **Frontend:** build estático Next.js o contenedor con `API_INTERNAL_URL` apuntando al backend interno.

## Cron de operaciones (ejemplo)

```cron
# Backup diario 02:00
0 2 * * * /opt/epintel/scripts/backup-postgres.sh >> /var/log/epintel-backup.log 2>&1

# Monitoreo drift cada 6 horas
0 */6 * * * API_URL=https://api.epintel.ejemplo.gov.co /opt/epintel/scripts/monitor-drift.sh || logger -t epintel-drift "drift check failed ($?)"
```

Programar `verify-backup-restore.sh` trimestralmente en ventana de mantenimiento.

## Observabilidad

- **Liveness:** `GET /health`
- **Métricas:** `GET /metrics` (Prometheus scrape)
- **Logs:** `LOG_JSON=true` en producción para agregación estructurada

OpenTelemetry queda como extensión post-MVP.

## Escalado inicial

Monolito modular: escalar réplicas del API detrás de balanceador; Postgres single-primary; worker de ingestión único para evitar carreras.

Ver también [`runbook-operations.md`](runbook-operations.md) y [`runbook-release.md`](runbook-release.md).
