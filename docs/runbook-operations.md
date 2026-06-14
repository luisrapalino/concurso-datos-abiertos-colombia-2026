# Runbook operativo (F9)

Procedimientos mínimos para respaldar y recuperar la base de datos del MVP.

## Backup programado (manual / cron del host)

```bash
./scripts/backup-postgres.sh
```

Variables opcionales:

| Variable | Default | Descripción |
|----------|---------|-------------|
| `BACKUP_DIR` | `./backups/postgres` | Directorio de salida |
| `BACKUP_RETENTION_DAYS` | `14` | Retención local en días |
| `COMPOSE` | `docker compose` | Comando Compose |

Ejemplo cron diario (02:00 UTC):

```cron
0 2 * * * cd /path/to/repo && ./scripts/backup-postgres.sh >> /var/log/epintel-backup.log 2>&1
```

## Restauración

```bash
./scripts/restore-postgres.sh backups/postgres/epintel_20260614T230000Z.sql.gz
docker compose restart api ingestion-worker
```

**Nota:** detén tráfico de escritura (API/worker) antes de restaurar en producción.

## Verificación trimestral

```bash
./scripts/verify-backup-restore.sh
```

Crea un volcado temporal, lo restaura en una base `epintel_restore_verify` y valida que existan observaciones curadas.

## Fallo de base de datos

1. Comprobar salud: `docker compose ps db`
2. Revisar logs: `docker compose logs db --tail=100`
3. Si el volumen está corrupto: restaurar último backup con `restore-postgres.sh`
4. Aplicar migraciones si hace falta: `docker compose exec api alembic upgrade head`

## Migración Alembic fallida

1. Revisar error en logs del servicio `api`
2. Corregir revisión en repo y generar fix forward (no editar historial ya aplicado en prod)
3. Restaurar backup previo a la migración si el esquema quedó inconsistente
4. Reintentar `alembic upgrade head` tras validar en entorno local

## Rollback de modelos ML

Ver [`runbook-release.md`](runbook-release.md).
