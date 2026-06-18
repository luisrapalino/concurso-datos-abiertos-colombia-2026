# Design system (MVP)

Guía visual para la interfaz institucional de inteligencia epidemiológica territorial.

## Principios

- Sobrio, legible, orientado a decisión analítica (no clínica).
- Identidad territorial: curvas de nivel sutiles, tipografía institucional.
- Estados vacíos y errores explícitos con orientación de acción.
- Frescura y límites de cobertura visibles.

## Paleta

| Token | Valor | Uso |
|-------|-------|-----|
| `--primary` | `#0a5c54` | Acciones, navegación activa, señal baja |
| `--background` | `#f0f5f3` | Fondo general (niebla verde) |
| `--foreground` | `#142824` | Texto principal (tinta bosque) |
| `--muted-foreground` | `#5c6f6b` | Texto secundario |
| `--border` | `#c8d9d4` | Contornos |
| `--signal` | `#b45309` | Alertas medias, proyecciones |
| `--destructive` | `#b42318` | Riesgo alto / crítico |
| `--sidebar` | `#0a3d38` | Barra lateral |

## Tipografía

- **Títulos**: Source Serif 4 — tono institucional de informe epidemiológico.
- **Cuerpo**: DM Sans — legible en tablas y filtros.
- **Datos**: JetBrains Mono — valores tabulares y señales numéricas.

## Elemento firma

- **Superficie topográfica** (`.topography-surface`): patrón de curvas de nivel en el área de contenido.
- **Anillo de señal** (`.signal-ring` + `SignalReadout`): lectura visual de la probabilidad de brote.

## Clasificación de riesgo

| Nivel | Color semántico |
|-------|-----------------|
| Bajo | `#0a5c54` |
| Medio | `#b45309` |
| Alto / Crítico | `#b42318` |

## Componentes base

Todos los elementos de interfaz usan **shadcn/ui v4** (`frontend/src/components/ui/`): Alert, Badge, Button, Calendar, Card, Combobox, Field, Popover, Separator, Sidebar, Skeleton, etc.

Los helpers de dominio para variantes de badge viven en `frontend/src/lib/risk-badges.ts`.

## Mapas

Leaflet con marcadores municipales (coordenadas DIVIPOLA), contornos departamentales GeoJSON (DANE MGN 2018) y color por clasificación de riesgo. Tema en `frontend/src/components/map/colombia-map-theme.ts` con variantes claro/oscuro vía `useMapTheme()`.

## Modo oscuro

- Activación: botón en la barra superior o preferencia del sistema (localStorage `radar-theme`).
- Tokens en `.dark` de `globals.css`; topografía y mapa adaptados.
- Gráficos ECharts usan `useChartTheme()` para colores coherentes.

## Motion (AnimatePresence)

Patrones en `frontend/src/components/motion/` y `frontend/src/lib/motion-presets.ts`, auditados con la skill `mastering-animate-presence`:

- `PageTransition` — cambio de ruta con `mode="wait"` y duración 150ms
- `ResourcePresence` — estados loading/error/empty/ready con exit simétrico
- `SignalCardPresence` — tarjeta de señal al cambiar municipio
- `PresenceShell` — desactiva interacciones durante exit (`useIsPresent`)
- Respeta `prefers-reduced-motion` vía `useReducedMotion()`

## Impresión y PDF

- Ruta `/informe` → **Imprimir informe** o **Exportar PDF** (diálogo del navegador → «Guardar como PDF»).
- Masthead institucional solo visible en impresión.
- Chrome de la app (sidebar, filtros, navegación) oculto vía `.app-chrome` y `print:hidden`.
- Formato A4 con márgenes definidos en `@page`.
