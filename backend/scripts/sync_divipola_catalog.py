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


def fetch_municipalities(*, timeout_seconds: float = 60.0) -> dict[str, dict[str, str]]:
    params = {
        "$select": "cod_mpio,cod_dpto,nom_mpio",
        "$where": "tipo_municipio='Municipio'",
        "$limit": 5000,
    }
    with httpx.Client(timeout=timeout_seconds) as client:
        response = client.get(DATASET_URL, params=params)
        response.raise_for_status()
        rows = response.json()

    municipalities: dict[str, dict[str, str]] = {}
    for row in rows:
        code = str(row["cod_mpio"]).zfill(5)
        municipalities[code] = {
            "department_code": str(row["cod_dpto"]).zfill(2),
            "name": str(row.get("nom_mpio", "")),
        }
    return municipalities


def build_catalog_payload(municipalities: dict[str, dict[str, str]]) -> dict[str, object]:
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
