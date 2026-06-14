#!/usr/bin/env python3
"""Download DANE DIVIPOLA municipality catalog from datos.gov.co."""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import httpx

DATASET_URL = "https://www.datos.gov.co/resource/gdxc-w37w.json"
DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "data" / "divipola_municipality_catalog.json"


def _parse_coordinate(raw_value: str | None) -> float | None:
    if not raw_value:
        return None
    normalized = str(raw_value).strip().replace(",", ".")
    try:
        return float(normalized)
    except ValueError:
        return None


def fetch_municipalities(*, timeout_seconds: float = 60.0) -> dict[str, dict[str, str | float]]:
    params = {
        "$select": "cod_mpio,cod_dpto,nom_mpio,latitud,longitud",
        "$where": "tipo_municipio='Municipio'",
        "$limit": 5000,
    }
    with httpx.Client(timeout=timeout_seconds) as client:
        response = client.get(DATASET_URL, params=params)
        response.raise_for_status()
        rows = response.json()

    municipalities: dict[str, dict[str, str | float]] = {}
    for row in rows:
        code = str(row["cod_mpio"]).zfill(5)
        latitude = _parse_coordinate(row.get("latitud"))
        longitude = _parse_coordinate(row.get("longitud"))
        entry: dict[str, str | float] = {
            "department_code": str(row["cod_dpto"]).zfill(2),
            "name": str(row.get("nom_mpio", "")),
        }
        if latitude is not None and longitude is not None:
            entry["latitude"] = latitude
            entry["longitude"] = longitude
        municipalities[code] = entry
    return municipalities


def build_catalog_payload(municipalities: dict[str, dict[str, str | float]]) -> dict[str, object]:
    return {
        "source_id": "dane-divipola",
        "dataset_url": DATASET_URL,
        "synced_at": datetime.now(tz=UTC).isoformat(),
        "municipality_count": len(municipalities),
        "municipalities": municipalities,
    }


def sync_catalog(output_path: Path = DEFAULT_OUTPUT) -> int:
    municipalities = fetch_municipalities()
    if not municipalities:
        msg = "DIVIPOLA catalog download returned no municipalities."
        raise RuntimeError(msg)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = build_catalog_payload(municipalities)
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {output_path} ({payload['municipality_count']} municipalities)")
    return payload["municipality_count"]


def main(argv: list[str] | None = None) -> int:
    output = DEFAULT_OUTPUT
    if argv and len(argv) > 1:
        output = Path(argv[1])
    sync_catalog(output)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
