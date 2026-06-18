from config.settings import get_settings
from modules.epidemiological_surveillance.application.municipality_dto import MunicipalityReadDto
from shared.divipola_catalog import DivipolaCatalog
from shared.featured_municipalities import FEATURED_MUNICIPALITIES


class SearchMunicipalitiesUseCase:
    """Lookup municipalities by DIVIPOLA code or name."""

    def __init__(self, catalog: DivipolaCatalog | None = None) -> None:
        settings = get_settings()
        self._catalog = catalog or DivipolaCatalog.from_file(settings.divipola_catalog_path)

    def execute(self, *, search: str, limit: int = 8) -> list[MunicipalityReadDto]:
        matches = self._catalog.search_municipalities(search, limit=limit)
        return [MunicipalityReadDto.model_validate(match) for match in matches]

    def list_featured(self) -> list[MunicipalityReadDto]:
        featured: list[MunicipalityReadDto] = []
        for entry in FEATURED_MUNICIPALITIES:
            catalog_entry = self._catalog.get_municipality(entry.territorial_code)
            name = str(catalog_entry.get("name", entry.name)) if catalog_entry else entry.name
            featured.append(
                MunicipalityReadDto(
                    territorial_code=entry.territorial_code,
                    name=name,
                    department_code=entry.department_code,
                    display_name=f"{name.title()} ({entry.territorial_code})",
                )
            )
        return featured

    def get_by_code(self, territorial_code: str) -> MunicipalityReadDto | None:
        entry = self._catalog.get_municipality(territorial_code)
        if entry is None:
            return None
        normalized_code = territorial_code.strip().zfill(5)
        name = str(entry.get("name", ""))
        return MunicipalityReadDto(
            territorial_code=normalized_code,
            name=name,
            department_code=str(entry.get("department_code", "")),
            display_name=f"{name.title()} ({normalized_code})",
        )
