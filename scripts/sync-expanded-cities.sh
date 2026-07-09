#!/usr/bin/env bash
# Sincroniza datos abiertos para las 20 ciudades destacadas (sin borrar observaciones previas).
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_CONTAINER="${API_CONTAINER:-concurso-datos-abiertos-colombia-2026-api-1}"
DB_CONTAINER="${DB_CONTAINER:-concurso-datos-abiertos-colombia-2026-db-1}"
PGUSER="${POSTGRES_USER:-epintel}"
PGDB="${POSTGRES_DB:-epintel}"
BATCH_SIZE="${INGESTION_BATCH_SIZE:-1000}"
START_YEAR="${INGESTION_START_YEAR:-2024}"
END_YEAR="${INGESTION_END_YEAR:-2018}"
EXPANDED_CODES="05001,11001,08001,76001,13001,68001,54001,66001,73001,47001,63001,52001,17001,23001,41001,19001,15001,50001,44001,20001"
LOG_DIR="${ROOT_DIR}/logs"
mkdir -p "${LOG_DIR}"
LOG_FILE="${LOG_DIR}/sync-expanded-cities.log"

exec > >(tee -a "${LOG_FILE}") 2>&1

echo "=== $(date -Iseconds) Sincronización ampliada (20 ciudades) ==="
echo "Años: ${START_YEAR} → ${END_YEAR} · batch=${BATCH_SIZE}"

docker exec "${API_CONTAINER}" \
  python -m modules.epidemiological_surveillance.interfaces.cli ingest-sync-municipal \
  --batch-size "${BATCH_SIZE}" \
  --start-year "${START_YEAR}" \
  --end-year "${END_YEAR}" \
  --territorial-codes "${EXPANDED_CODES}"

echo "=== Resumen por definición ==="
docker exec "${DB_CONTAINER}" psql -U "${PGUSER}" -d "${PGDB}" -c "
SELECT definition_id, COUNT(*) AS n, COUNT(DISTINCT territorial_code) AS municipios
FROM health_indicator_observations
GROUP BY definition_id
ORDER BY n DESC;
"

echo "=== Total observaciones ==="
docker exec "${DB_CONTAINER}" psql -U "${PGUSER}" -d "${PGDB}" -c "
SELECT COUNT(*) AS total, COUNT(DISTINCT territorial_code) AS municipios
FROM health_indicator_observations;
"

echo "=== $(date -Iseconds) Sincronización ampliada completada ==="
