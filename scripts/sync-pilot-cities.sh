#!/usr/bin/env bash
# Limpia la BD y re-captura datos abiertos solo para las 4 ciudades piloto.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_CONTAINER="${API_CONTAINER:-concurso-datos-abiertos-colombia-2026-api-1}"
DB_CONTAINER="${DB_CONTAINER:-concurso-datos-abiertos-colombia-2026-db-1}"
PGUSER="${POSTGRES_USER:-epintel}"
PGDB="${POSTGRES_DB:-epintel}"
BATCH_SIZE="${INGESTION_BATCH_SIZE:-1000}"
START_YEAR="${INGESTION_START_YEAR:-2022}"
END_YEAR="${INGESTION_END_YEAR:-2015}"
PILOT_CODES="05001,11001,08001,76001"
LOG_DIR="${ROOT_DIR}/logs"
mkdir -p "${LOG_DIR}"
LOG_FILE="${LOG_DIR}/sync-pilot-cities.log"

exec > >(tee -a "${LOG_FILE}") 2>&1

echo "=== $(date -Iseconds) Piloto: Medellín, Bogotá, Barranquilla, Cali ==="

"${ROOT_DIR}/scripts/clean-pilot-data.sh"

echo "=== Sincronizando fuentes (${START_YEAR}→${END_YEAR}) ==="
docker exec "${API_CONTAINER}" \
  python -m modules.epidemiological_surveillance.interfaces.cli ingest-sync-municipal \
  --batch-size "${BATCH_SIZE}" \
  --start-year "${START_YEAR}" \
  --end-year "${END_YEAR}" \
  --territorial-codes "${PILOT_CODES}"

echo "=== Recorte final a municipios piloto ==="
docker exec "${DB_CONTAINER}" psql -U "${PGUSER}" -d "${PGDB}" -v ON_ERROR_STOP=1 <<SQL
DELETE FROM health_indicator_observations
WHERE territorial_code NOT IN ('05001', '11001', '08001', '76001');
DELETE FROM outbreak_predictions
WHERE territorial_code NOT IN ('05001', '11001', '08001', '76001');
DELETE FROM territorial_risk_scores
WHERE territorial_code NOT IN ('05001', '11001', '08001', '76001');
SQL

echo "=== Resumen por definición ==="
docker exec "${DB_CONTAINER}" psql -U "${PGUSER}" -d "${PGDB}" -c "
SELECT definition_id, COUNT(*) AS n, COUNT(DISTINCT territorial_code) AS municipios
FROM health_indicator_observations
GROUP BY definition_id
ORDER BY n DESC;
"

echo "=== $(date -Iseconds) Captura piloto completada ==="
