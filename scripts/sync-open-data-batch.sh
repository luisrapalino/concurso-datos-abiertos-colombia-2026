#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_CONTAINER="${API_CONTAINER:-concurso-datos-abiertos-colombia-2026-api-1}"
BATCH_SIZE="${INGESTION_BATCH_SIZE:-1000}"
START_YEAR="${INGESTION_START_YEAR:-2022}"
END_YEAR="${INGESTION_END_YEAR:-2015}"

echo "Sincronización piloto: Medellín, Bogotá, Barranquilla, Cali"
echo "Delegando en scripts/sync-pilot-cities.sh (limpia + captura)"

exec "${ROOT_DIR}/scripts/sync-pilot-cities.sh"
