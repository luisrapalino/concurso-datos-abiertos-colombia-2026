#!/usr/bin/env python3
"""Export OpenAPI schema for frontend type generation."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://epintel:epintel@localhost:5432/epintel",
)

from api.main import create_app

DEFAULT_OUTPUT = Path(__file__).resolve().parents[2] / "openapi" / "openapi.json"


def export_openapi(output_path: Path = DEFAULT_OUTPUT) -> Path:
    app = create_app()
    schema = app.openapi()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
    return output_path


def main(argv: list[str] | None = None) -> int:
    output = DEFAULT_OUTPUT
    if argv and len(argv) > 1:
        output = Path(argv[1])
    path = export_openapi(output)
    print(f"Wrote OpenAPI schema to {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
