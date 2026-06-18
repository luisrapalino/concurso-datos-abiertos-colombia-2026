#!/usr/bin/env bash
set -euo pipefail

API_URL="${API_URL:-http://localhost:8000}"
DEFINITION_ID="${DEFINITION_ID:-general-mortality-rate}"

response="$(curl -fsS "${API_URL}/api/v1/data-drift?definition_id=${DEFINITION_ID}")"
status="$(echo "${response}" | python3 -c 'import json,sys; print(json.load(sys.stdin)["drift_status"])')"

echo "data-drift status=${status}"

case "${status}" in
  alert)
    echo "ALERT: data drift requires attention." >&2
    exit 2
    ;;
  warning)
    echo "WARNING: data drift elevated." >&2
    exit 1
    ;;
  stable)
    exit 0
    ;;
  *)
    echo "UNKNOWN drift status." >&2
    exit 3
    ;;
esac
