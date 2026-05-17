# Plataforma de Inteligencia Epidemiológica Territorial

Directorio de aplicación y documentación del proyecto.

## Desarrollo (Docker)

1. Copia variables de entorno: `Copy-Item .env.example .env` (ajusta si hace falta).
2. Desde esta carpeta (`app/`): `docker compose up --build`.
3. El contenedor `api` ejecuta **Alembic** (`upgrade head`) antes de arrancar Uvicorn.
4. Comprueba: [http://localhost:8000/health](http://localhost:8000/health), [http://localhost:8000/docs](http://localhost:8000/docs), datos persistidos en [http://localhost:8000/api/v1/health-indicators](http://localhost:8000/api/v1/health-indicators).

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

**Siguiente paso sugerido:** capa de ingestión o siguiente recurso REST versionado; frontend Next.js cuando quieras cerrar el vertical slice.

## Convenciones para agentes

- [.cursor/skills/atomic-commits/](.cursor/skills/atomic-commits/) — skill de **commits atómicos** (un propósito por commit, Conventional Commits).

## Documentación

- [AGENTS.md](AGENTS.md) — visión del producto, stack, arquitectura (DDD), reglas de backend, frontend y ML, y convenciones de API.
- [docs/roadmap.md](docs/roadmap.md) — plan por fases hasta producto mínimo institucional completo.
- [docs/crisp-ml.md](docs/crisp-ml.md) — ciclo de vida del sistema de IA y calidad (CRISP-ML(Q)).
