#!/usr/bin/env bash
# Smoke test: backup → restore into a temporary database inside the db container.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

COMPOSE="${COMPOSE:-docker compose}"
DB_SERVICE="${DB_SERVICE:-db}"
DB_USER="${POSTGRES_USER:-epintel}"
VERIFY_DB="${VERIFY_DB:-epintel_restore_verify}"

backup_file="$(mktemp --suffix=.sql.gz)"
trap 'rm -f "$backup_file"' EXIT

echo "Step 1/3: creating temporary backup..."
$COMPOSE exec -T "$DB_SERVICE" pg_dump -U "$DB_USER" -d epintel --no-owner --no-acl | gzip > "$backup_file"

echo "Step 2/3: restoring into verification database '$VERIFY_DB'..."
$COMPOSE exec -T "$DB_SERVICE" psql -U "$DB_USER" -d postgres -v ON_ERROR_STOP=1 \
  -c "DROP DATABASE IF EXISTS $VERIFY_DB;" \
  -c "CREATE DATABASE $VERIFY_DB OWNER $DB_USER;" >/dev/null

gunzip -c "$backup_file" | $COMPOSE exec -T "$DB_SERVICE" psql -U "$DB_USER" -d "$VERIFY_DB" -v ON_ERROR_STOP=1 >/dev/null

echo "Step 3/3: checking curated observations count..."
count="$($COMPOSE exec -T "$DB_SERVICE" psql -U "$DB_USER" -d "$VERIFY_DB" -tAc \
  "SELECT COUNT(*) FROM health_indicator_observations;" | tr -d '[:space:]')"

$COMPOSE exec -T "$DB_SERVICE" psql -U "$DB_USER" -d postgres -v ON_ERROR_STOP=1 \
  -c "DROP DATABASE $VERIFY_DB;" >/dev/null

echo "Verification database row count: $count"
if [[ -z "$count" ]] || [[ "$count" -eq 0 ]]; then
  echo "Restore verification failed: no curated observations found." >&2
  exit 1
fi

echo "Backup/restore verification passed."
