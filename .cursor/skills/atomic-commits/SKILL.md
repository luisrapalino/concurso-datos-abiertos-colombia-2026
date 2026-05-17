---
name: atomic-commits
description: >-
  Creates small, single-purpose git commits with clear Conventional Commit
  messages. Use when the user asks to commit, split changes into commits,
  write commit messages, or mentions atomic commits, git history, or staging.
---

# Commits atómicos

## Cuándo aplicar

- El usuario pide **commitear**, **hacer commit** o **dejar el historial limpio**.
- Hay cambios mezclados (feature + docs + formato) que deben **separarse**.
- Antes de cualquier `git commit`, aunque el usuario no diga "atómico".

**No commitear** salvo petición explícita del usuario (regla del proyecto).

---

## Qué es un commit atómico

Un commit = **un cambio lógico completo** que:

1. Tiene **un solo propósito** (un fix, una feature acotada, solo docs, solo infra).
2. Deja el repo en un estado **consistente** (build/tests razonables para ese alcance).
3. Se puede **revertir** sin arrastrar cambios no relacionados.
4. El mensaje describe **por qué** importa, no solo qué archivos tocó.

Si el diff mezcla propósitos → **varios commits**, no uno grande.

---

## Flujo obligatorio antes de commitear

1. `git status` y `git diff` (staged + unstaged).
2. Clasificar cada hunk: ¿mismo propósito?
3. Si hay mezcla → **staging parcial** (`git add -p` o archivos concretos) y commits en orden lógico.
4. Redactar mensaje (formato abajo).
5. Un commit por propósito; `git status` limpio para lo acordado.

**Nunca** incluir: `.env`, credenciales, `__pycache__`, `.venv`, artefactos de build, datos sensibles.

---

## Cómo dividir cambios

| Señal | Acción |
|--------|--------|
| Código + documentación no ligada al mismo cambio | Commit de código; commit `docs:` aparte |
| Refactor + comportamiento nuevo | Primero `refactor:` (sin cambiar comportamiento); luego `feat:` o `fix:` |
| Migración DB + lógica que la usa | Migración (`chore(db):` o `feat:`); luego código que depende |
| Formato/lint masivo + feature | `style:` o `chore:` solo formato; feature en otro commit |
| Varios módulos independientes | Un commit por módulo o por vertical slice |

Orden sugerido: **infra/config → dominio → API → tests → docs** cuando haya dependencia.

---

## Formato del mensaje

**Conventional Commits** (asunto en inglés, imperativo, ≤72 caracteres):

```
<tipo>(<ámbito opcional>): <resumen en imperativo>

[Cuerpo opcional: por qué, no repetir el diff. En español si el usuario prefiere.]

[Footer opcional: Breaking change:, Refs #123]
```

**Tipos habituales:** `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `build`, `ci`, `style`.

**Ámbito:** acorde al repo (`backend`, `frontend`, `db`, `docker`, `api`, módulo de dominio).

**Ejemplos:**

```
feat(backend): persist health indicators with SQLAlchemy repository

docs: add implementation roadmap for institutional MVP
```

```
fix(api): initialize database engine on application lifespan
```

```
chore(docker): run Alembic migrations before Uvicorn startup
```

Evitar mensajes vagos: `update`, `fix stuff`, `WIP`, `changes`.

---

## Checklist rápido

- [ ] Un solo propósito por commit
- [ ] Sin secretos ni basura en el stage
- [ ] Mensaje explica el **por qué** en el cuerpo si no es obvio
- [ ] Si el usuario pidió varios commits, no squashar sin permiso
- [ ] No `--no-verify`, no `push --force` a main, no amend salvo reglas del usuario

---

## Seguridad git (resumen)

- No modificar `git config`.
- No amend si el commit no es tuyo en esta sesión o ya fue pusheado (salvo petición explícita).
- Si un hook falla: corregir y **nuevo commit**, no amend del fallido.

Más ejemplos de división: [examples.md](examples.md).
