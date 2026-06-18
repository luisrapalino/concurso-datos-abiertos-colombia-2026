#!/usr/bin/env bash
# Limpia observaciones, predicciones y corridas de ingesta.
set -euo pipefail

CONTAINER="${DB_CONTAINER:-concurso-datos-abiertos-colombia-2026-db-1}"
PGUSER="${POSTGRES_USER:-epintel}"
PGDB="${POSTGRES_DB:-epintel}"

echo "Limpiando datos analíticos en PostgreSQL…"

docker exec "${CONTAINER}" psql -U "${PGUSER}" -d "${PGDB}" -v ON_ERROR_STOP=1 <<'SQL'
TRUNCATE TABLE outbreak_predictions;
TRUNCATE TABLE territorial_risk_scores;
TRUNCATE TABLE health_indicator_observations;
TRUNCATE TABLE ingestion_runs;
SQL

echo "Limpieza completada."
