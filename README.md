# Plataforma de Inteligencia Epidemiológica Territorial

Plataforma de inteligencia epidemiológica territorial basada en **datos abiertos** e **IA explicable** para apoyar la toma de decisiones en salud pública.

**Concurso de Datos Abiertos Colombia 2026** — nivel **Intermedio (IA)**  
Reto: predecir brotes de enfermedades transmisibles integrando morbilidad, vacunación, calidad del aire y acceso a salud.

| Aspecto | Detalle |
|---------|---------|
| **Equipo ID** | 200 |
| **Reto** | Salud y Bienestar — brotes transmisibles con IA |
| Modelo principal | `randomforest-outbreak-v1.0.0` (Random Forest + SHAP) |
| Variables ML | 15 features multivariadas |
| Fuentes abiertas | 4–5 conjuntos [datos.gov.co](https://www.datos.gov.co) |
| Validación | Split temporal train ≤2020 / test ≥2021 |
| Trazabilidad concurso | [`docs/concurso-alignment.md`](docs/concurso-alignment.md) |

### Equipo

| Rol | Contacto |
|-----|----------|
| Líder | luisrapalino88@gmail.com |
| Participante 2 | Rapalinorokate@gmail.com 
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

Los códigos municipales se validan contra el catálogo DANE DIVIPOLA embebido (`backend/data/`). Worker programado:

```bash
docker compose up -d ingestion-worker
```

## Modelos ML — brotes (reto concurso)

Entrenar, promover y servir predicciones con SHAP:

```bash
cd backend
PYTHONPATH=src python ml/train_outbreak_experiment.py --from-db
PYTHONPATH=src python -m modules.outbreak_prediction.interfaces.ml_cli promote randomforest-outbreak-v1.0.0
PYTHONPATH=src python -m modules.outbreak_prediction.interfaces.ml_cli status
```

Rollback al scoring rule-based:

```bash
PYTHONPATH=src python -m modules.outbreak_prediction.interfaces.ml_cli rollback
```

Ver [`docs/ml-evaluation.md`](docs/ml-evaluation.md) y [`docs/data-dictionary.md`](docs/data-dictionary.md).

## Modelos ML — riesgo territorial (contexto)

```bash
cd backend
PYTHONPATH=src python ml/train_mortality_experiment.py
PYTHONPATH=src python -m modules.territorial_risk.interfaces.ml_cli promote ridge-mortality-risk-v1.0.0
PYTHONPATH=src python -m modules.territorial_risk.interfaces.ml_cli rollback
```

## Backups PostgreSQL

```bash
./scripts/backup-postgres.sh
./scripts/verify-backup-restore.sh   # prueba periódica
```

Ver [`docs/runbook-operations.md`](docs/runbook-operations.md).

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

- [docs/concurso-alignment.md](docs/concurso-alignment.md) — trazabilidad con el reto del concurso (nivel Intermedio).
- [docs/data-dictionary.md](docs/data-dictionary.md) — 15 variables del modelo de brotes.
- [docs/data-sources.md](docs/data-sources.md) — catálogo de fuentes datos.gov.co.
- [docs/ml-evaluation.md](docs/ml-evaluation.md) — evaluación, validación temporal, ciclo promote/rollback.
- [AGENTS.md](AGENTS.md) — visión del producto, stack, arquitectura (DDD), reglas de backend, frontend y ML.
- [docs/roadmap.md](docs/roadmap.md) — plan por fases hasta producto mínimo institucional completo.
- [docs/user-guide.md](docs/user-guide.md) — guía de uso del MVP.
- [docs/architecture.md](docs/architecture.md) — arquitectura técnica resumida.
- [docs/crisp-ml.md](docs/crisp-ml.md) — ciclo de vida del sistema de IA y calidad (CRISP-ML(Q)).

## Licencia

Código bajo [MIT](LICENSE). Los datasets de [datos.gov.co](https://www.datos.gov.co) conservan sus propias condiciones de uso.
