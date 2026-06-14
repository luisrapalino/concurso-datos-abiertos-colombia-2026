import json
from pathlib import Path

from config.settings import Settings, get_settings


class GetTerritorialBoundariesUseCase:
    """Serves static GeoJSON boundaries aligned with DANE MGN 2018."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    def execute(self, *, level: str = "department") -> dict[str, object]:
        if level != "department":
            msg = "Only department-level boundaries are available in the MVP."
            raise ValueError(msg)

        geojson_path = self._resolve_geojson_path(level)
        return json.loads(geojson_path.read_text(encoding="utf-8"))

    def _resolve_geojson_path(self, level: str) -> Path:
        del level
        if self._settings.geojson_data_dir is not None:
            return self._settings.geojson_data_dir / "colombia_departments.geojson"
        backend_root = Path(__file__).resolve().parents[4]
        return backend_root / "data" / "colombia_departments.geojson"
