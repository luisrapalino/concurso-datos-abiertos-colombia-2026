# Guía de usuario

**Radar de brotes** — vigilancia temprana con datos abiertos de Colombia.

## Acceso

| Servicio | URL local |
|----------|-----------|
| Frontend | http://localhost:3002 |
| API | http://localhost:8000/docs |

## Las 4 vistas (todo lo que necesitas)

1. **Radar** (`/`) — ¿Qué municipios revisar primero? Ranking cruzando **6 enfermedades transmisibles** (dengue, chikungunya, dengue grave, hepatitis A/B, fiebre tifoidea).
2. **Ficha** (`/brotes`) — Detalle explicado para un municipio, enfermedad y semana epidemiológica.
3. **Mapa** (`/mapa`) — Señales geográficas por enfermedad en ciudades principales.
4. **Informe** (`/informe`) — PDF imprimible para reuniones de vigilancia.

## Filtros

- **Enfermedad** — selecciona el evento SIVIGILA (código INS).
- **Municipio** — busca por nombre o código DANE.
- **Semana epidemiológica** — periodo ISO de la señal.

## Flujo recomendado

1. Abre el **Radar** y mira el ranking de la semana.
2. Haz clic en **Ver ficha** del municipio que te interese.
3. Usa el **Mapa** para contexto geográfico.
4. Genera el **Informe** si necesitas compartir en una reunión.

## Interpretación responsable

- La señal **prioriza revisión humana**; no confirma brote ni activa respuesta automática.
- Los datos dependen de lo publicado en [datos.gov.co](https://www.datos.gov.co).
- La sincronización es **nacional por lotes** (municipio → año → páginas de 1 000). Hay un script por enfermedad o grupo:
  - `./scripts/sync-sivigila-diseases.sh` — las 6 enfermedades
  - `./scripts/sync-sivigila-diseases.sh chikungunya hepatitis-a` — solo las que indiques
  - Logs en `logs/sync-sivigila-<enfermedad>.log`

Más detalle técnico: [`concurso-alignment.md`](concurso-alignment.md), [`data-sources.md`](data-sources.md).
