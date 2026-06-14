# Plataforma de Inteligencia Epidemiológica Territorial

Directorio de aplicación y documentación del proyecto.

## Desarrollo (Docker)

1. Copia variables de entorno: `cp .env.example .env` (ajusta puertos si hay conflictos locales).
2. Desde la raíz del repositorio: `docker compose up --build`.
3. Frontend: [http://localhost:3000](http://localhost:3000) · API: [http://localhost:8000/docs](http://localhost:8000/docs).
4. El contenedor `api` ejecuta **Alembic** (`upgrade head`) antes de arrancar Uvicorn.

Si el puerto **5432** o **3000** están ocupados, copia `docker-compose.override.example.yml` a `docker-compose.override.yml` (ignorado por git) para mapear Postgres a **5433** y la web a **3002**.

## Ingestión multi-año

```bash
cd backend
PYTHONPATH=src python -m modules.epidemiological_surveillance.interfaces.cli ingest \
  datos-gov-mortality-indicators --years 2018,2019,2020 --limit 15000
```

`DATABASE_URL` debe usar el driver **psycopg v3**, por ejemplo `postgresql+psycopg://epintel:epintel@db:5432/epintel` (ya definido en `docker-compose.yml` para el servicio `api`).

## Desarrollo local del backend (sin reconstruir imagen)

Con PostgreSQL accesible y entorno virtual con dependencias instaladas desde `backend/requirements.txt`:

```powershell
Set-Location backend
$env:PYTHONPATH = "src"
$env:DATABASE_URL = "postgresql+psycopg://epintel:epintel@localhost:5432/epintel"
python -m alembic -c alembic.ini upgrade head
python -m uvicorn api.main:app --reload --app-dir src
```

Nota: `--app-dir src` permite que Uvicorn resuelva el paquete `api` con `PYTHONPATH=src`.

## Arquitectura backend (resumen)

- `backend/src/api` — FastAPI, lifespan (motor SQLAlchemy), dependencias HTTP.
- `backend/src/config` — ajustes (`DATABASE_URL` → `database_url` vía Pydantic Settings).
- `backend/src/infrastructure/persistence` — motor, sesión y `Base` declarativo.
- `backend/src/modules/health_indicators` — dominio (`HealthIndicator`, `HealthIndicatorRepository`), aplicación (caso de uso + DTO), infraestructura (ORM + repositorio SQLAlchemy), interfaces (router).

Migraciones: `backend/alembic` + `backend/alembic.ini`.

**Siguiente paso sugerido:** etiquetar release MVP (`docs/runbook-release.md`) e ingestión multi-año para enriquecer tendencias.

## Documentación

- [AGENTS.md](AGENTS.md) — visión del producto, stack, arquitectura (DDD), reglas de backend, frontend y ML, y convenciones de API.
- [docs/roadmap.md](docs/roadmap.md) — plan por fases hasta producto mínimo institucional completo.
- [docs/user-guide.md](docs/user-guide.md) — guía de uso del MVP.
- [docs/architecture.md](docs/architecture.md) — arquitectura técnica resumida.
- [docs/crisp-ml.md](docs/crisp-ml.md) — ciclo de vida del sistema de IA y calidad (CRISP-ML(Q)).
