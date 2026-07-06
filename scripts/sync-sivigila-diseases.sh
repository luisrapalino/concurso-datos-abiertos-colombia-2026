#!/usr/bin/env bash
# Sincroniza enfermedades SIVIGILA para las 4 ciudades piloto.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_CONTAINER="${API_CONTAINER:-concurso-datos-abiertos-colombia-2026-api-1}"
BATCH_SIZE="${INGESTION_BATCH_SIZE:-1000}"
START_YEAR="${INGESTION_START_YEAR:-2022}"
END_YEAR="${INGESTION_END_YEAR:-2018}"
PILOT_CODES="05001,11001,08001,76001"
LOG_DIR="${ROOT_DIR}/logs"
mkdir -p "${LOG_DIR}"

ALL_SLUGS=(dengue chikungunya dengue-grave hepatitis-a hepatitis-b typhoid)
SLUGS=("${@:-${ALL_SLUGS[@]}}")

for slug in "${SLUGS[@]}"; do
  log="${LOG_DIR}/sync-sivigila-${slug}.log"
  echo "=== $(date -Iseconds) datos-gov-sivigila-${slug} (piloto) ===" | tee -a "${log}"
  docker exec "${API_CONTAINER}" \
    python -m modules.epidemiological_surveillance.interfaces.cli ingest-sync \
    "datos-gov-sivigila-${slug}" \
    --batch-size "${BATCH_SIZE}" \
    --start-year "${START_YEAR}" \
    --end-year "${END_YEAR}" \
    --territorial-codes "${PILOT_CODES}" \
    2>&1 | tee -a "${log}"
done
