from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    log_json: bool = False
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 120
    divipola_catalog_path: Path | None = None
    ingestion_schedule_enabled: bool = False
    ingestion_interval_hours: int = 24
    ingestion_default_years: str = "2018,2019,2020"
    ingestion_default_limit: int = 15000
    ingestion_validate_territorial_codes: bool = True
    ml_artifacts_dir: Path | None = None
    geojson_data_dir: Path | None = None

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
