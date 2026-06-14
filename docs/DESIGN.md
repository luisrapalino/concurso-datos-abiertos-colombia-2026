# Design system (MVP)

Guía visual mínima para la interfaz institucional.

## Principios

- Sobrio, legible, orientado a decisión analítica (no clínica).
- Estados vacíos y errores explícitos.
- Frescura y límites de cobertura visibles.

## Paleta

| Token | Light | Uso |
|-------|-------|-----|
| `--primary` | `#0f766e` | Acciones, navegación activa |
| `--background` | `#f8fafc` | Fondo general |
| `--foreground` | `#0f172a` | Texto principal |
| `--muted-foreground` | `#64748b` | Texto secundario |
| `--border` | `#e2e8f0` | Contornos |

## Tipografía

- Sans: Geist (Next.js)
- Mono: Geist Mono para valores tabulares

## Clasificación de riesgo

| Nivel | Color semántico |
|-------|-----------------|
| Bajo | Verde |
| Medio | Ámbar |
| Alto / Crítico | Rojo |

## Componentes base

Botones, tarjetas, badges e inputs viven en `frontend/src/components/ui/`.

## Mapas

Leaflet con marcadores circulares coloreados por clasificación de riesgo; centroides departamentales en MVP.
