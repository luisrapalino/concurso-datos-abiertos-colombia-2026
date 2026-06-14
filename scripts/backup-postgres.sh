#!/usr/bin/env bash
# Backup PostgreSQL del stack Docker Compose (servicio db).
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

BACKUP_DIR="${BACKUP_DIR:-$ROOT_DIR/backups/postgres}"
COMPOSE="${COMPOSE:-docker compose}"
DB_SERVICE="${DB_SERVICE:-db}"
DB_USER="${POSTGRES_USER:-epintel}"
DB_NAME="${POSTGRES_DB:-epintel}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-14}"

mkdir -p "$BACKUP_DIR"
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
backup_file="$BACKUP_DIR/${DB_NAME}_${timestamp}.sql.gz"

echo "Creating backup: $backup_file"
$COMPOSE exec -T "$DB_SERVICE" pg_dump -U "$DB_USER" -d "$DB_NAME" --no-owner --no-acl | gzip > "$backup_file"

if [[ ! -s "$backup_file" ]]; then
  echo "Backup failed: empty file $backup_file" >&2
  exit 1
fi

echo "Backup completed ($(du -h "$backup_file" | awk '{print $1}'))"

if [[ "$RETENTION_DAYS" =~ ^[0-9]+$ ]] && (( RETENTION_DAYS > 0 )); then
  find "$BACKUP_DIR" -name "${DB_NAME}_*.sql.gz" -type f -mtime +"$RETENTION_DAYS" -delete
  echo "Retention applied: ${RETENTION_DAYS} days"
fi
