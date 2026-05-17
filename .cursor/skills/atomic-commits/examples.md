# Ejemplos: commits atómicos

## Malo (un solo commit)

Cambios en el mismo commit:

- `backend/src/modules/.../repository.py` (feature)
- `docs/roadmap.md` (documentación)
- `README.md` (instrucciones Docker)
- `.gitignore` (chore)

**Problema:** revertir la feature arrastra docs y viceversa.

---

## Bueno (cuatro commits)

```text
chore: add Python and env patterns to gitignore

docs: add implementation roadmap for all project phases

feat(backend): add SQLAlchemy persistence for health indicators

docs: document Docker workflow and local backend setup
```

---

## Refactor + fix en el mismo archivo

**Mal:** un commit `fix: repository and cleanup`.

**Bien:**

1. `refactor(backend): extract session dependency for health indicators module`
2. `fix(backend): close database session on request teardown`

Solo si el refactor es independiente y el árbol compila entre commits; si no, un único commit `fix` con cuerpo que liste ambos aspectos **solo cuando no se puedan separar sin estado roto**.

---

## Migración + código

1. `feat(db): add health_indicators table and seed row`
2. `feat(backend): read health indicators from database repository`

El primero solo `alembic/versions/...`; el segundo solo capa de aplicación e infra que usa la tabla.

---

## Staging parcial (PowerShell)

```powershell
git add backend/src/modules/health_indicators/infrastructure/
git commit -m "feat(backend): add SQLAlchemy health indicator repository"

git add backend/alembic/versions/
git commit -m "feat(db): create health_indicators table"
```

Si el orden importa (migración antes que código), commitear en ese orden.
