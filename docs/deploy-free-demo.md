# Deploy gratuito para la sustentación

Receta 100% gratis para dejar la plataforma en línea durante la sustentación.

| Componente                  | Servicio                  | Notas                                                      |
| --------------------------- | ------------------------- | ---------------------------------------------------------- |
| Base de datos (Postgres 16) | **Neon** (free)           | Persistente. Se siembra una sola vez con un dump local.    |
| API (FastAPI + ML)          | **Render** (free, Docker) | Duerme tras ~15 min de inactividad; despertar tarda ~50 s. |
| Frontend (Next.js)          | **Vercel** (free)         | Proxy `/api/v1` → API (sin problemas de CORS).             |

> El navegador siempre llama a `/api/v1/...` en el mismo dominio de Vercel, y Next
> reenvía la petición a la API vía `API_INTERNAL_URL` (rewrite). Por eso **no hay
> CORS** desde el navegador. Como `API_INTERNAL_URL` se congela en build, hay que
> desplegar primero la API (Render) y luego el frontend (Vercel).

---

## 0. Requisitos

- Repo publicado en GitHub (ya lo está).
- Docker corriendo en local con la base ya cargada (~9.000 observaciones).
- Cuentas gratuitas: [Neon](https://neon.tech), [Render](https://render.com), [Vercel](https://vercel.com) (todas permiten registro con GitHub).

---

## 1. Base de datos — Neon

1. Crea un proyecto en Neon (región `AWS us-east` o la más cercana). Postgres 16/17.
2. Copia la **connection string** (formato `postgresql://USER:PASS@HOST/DB?sslmode=require`).
3. Guarda dos variantes:
   - **Para pg_restore (libpq):** tal cual la da Neon.
     `postgresql://USER:PASS@HOST/DB?sslmode=require`
   - **Para la API (psycopg v3):** cambia el esquema a `postgresql+psycopg://…`
     `postgresql+psycopg://USER:PASS@HOST/DB?sslmode=require`

---

## 2. Sembrar datos — dump local → Neon

En PowerShell, **no uses `>`** para volcados binarios (corrompe el archivo). Genera el
dump dentro del contenedor y cópialo con `docker compose cp`.

```powershell
# 1) Dump binario (custom format) desde la base local, dentro del contenedor db
docker compose exec db pg_dump -U epintel -d epintel -Fc --no-owner --no-privileges -f /tmp/epintel.dump

# 2) Copiar el dump al host
docker compose cp db:/tmp/epintel.dump ./epintel.dump

# 3) Restaurar en Neon usando un cliente Postgres 16 (contenedor efímero)
#    Reemplaza la URL por la connection string libpq de Neon (sslmode=require)
docker run --rm -v "${PWD}:/wd" postgres:16-alpine `
  pg_restore --no-owner --no-privileges --clean --if-exists `
  -d "postgresql://USER:PASS@HOST/DB?sslmode=require" /wd/epintel.dump
```

El dump incluye la tabla `alembic_version`, por lo que cuando la API arranque en
Render, `alembic upgrade head` no hará cambios (ya está en la última versión).

Verifica que hay datos:

```powershell
docker run --rm postgres:16-alpine `
  psql "postgresql://USER:PASS@HOST/DB?sslmode=require" `
  -c "select count(*) from health_indicator_observations;"
```

---

## 3. API — Render

1. En Render: **New → Blueprint** y apunta al repo. Detectará `render.yaml`.
   (Alternativa: **New → Web Service**, runtime Docker, Root Directory `backend`.)
2. En **Environment**, define las variables (marcadas `sync: false`):
   - `DATABASE_URL` = cadena **psycopg** de Neon
     (`postgresql+psycopg://USER:PASS@HOST/DB?sslmode=require`)
   - `CORS_ORIGINS` = URL del frontend en Vercel (la sabrás en el paso 4;
     puedes poner un placeholder y ajustarlo luego).
   - `SOCRATA_APP_TOKEN` = _(opcional, solo si ingestas en vivo)_
3. Deploy. Render construye la imagen (pesada por Prophet/SHAP; la primera build
   tarda varios minutos). No definas `PORT`: Render lo inyecta y el contenedor ya
   lo respeta (`--port ${PORT:-8000}`).
4. Cuando termine, prueba: `https://epintel-api.onrender.com/health` → `{"status":"ok"}`
   y `https://epintel-api.onrender.com/docs`.

---

## 4. Frontend — Vercel

1. En Vercel: **Add New → Project** e importa el repo.
2. **Root Directory:** `frontend`. Framework: Next.js (autodetectado).
3. **Environment Variables** (Production):
   - `API_INTERNAL_URL` = `https://epintel-api.onrender.com`
   - `NEXT_PUBLIC_API_URL` = `https://epintel-api.onrender.com`
4. Deploy. Copia la URL final (`https://tu-app.vercel.app`).
5. Vuelve a Render y pon esa URL en `CORS_ORIGINS`.

> Si cambias la URL de la API, hay que **redeploy** del frontend (el rewrite se
> resuelve en build).

---

## 5. Día de la sustentación (checklist)

- [ ] 3–5 min antes: abre `…onrender.com/health` para **despertar** la API (evita el cold start en vivo).
- [ ] Abre el frontend de Vercel y navega `/brotes`, `/mapa`, `/informe`.
- [ ] Caso de referencia: municipio `05001` (Medellín), periodo `2020-01`.
- [ ] Ten a mano `…onrender.com/docs` para mostrar la API.

---

## Notas y límites del free tier

- **Cold start (Render):** la API duerme tras ~15 min sin tráfico. Despertar ~50 s.
  Mitigación: warm-up manual antes de presentar.
- **RAM (Render free, 512 MB):** la imagen trae Prophet + SHAP + sklearn. La
  inferencia del modelo de brotes (RandomForest) es liviana, pero si hubiese
  problemas de memoria, considerar Hugging Face Space (Docker, más RAM) para la API.
- **Neon** no expira y mantiene los datos entre reinicios de la API.
