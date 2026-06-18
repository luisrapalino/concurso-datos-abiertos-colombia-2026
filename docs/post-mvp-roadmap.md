# Roadmap post-MVP

Extensiones sugeridas tras el hito institucional inicial (`v0.3.0-mvp`).

## Completado en MVP / cierre F10

- Ingestión automática programada (cron/worker Docker)
- Validación cruzada de códigos territoriales (DIVIPOLA)
- SHAP en serving para modelos promovidos
- Evaluación temporal (`evaluate_temporal.py` con `--from-db`)
- Análisis de sesgo por departamento (`/bias-analysis`)
- GeoJSON departamental en mapa + puntos municipales DIVIPOLA
- Exportación de informe territorial imprimible (`/informe`, `/territorial-report`)
- Backups Postgres + script de verificación de restauración
- Alertas de drift básicas (`/data-drift`, `scripts/monitor-drift.sh`)
- API key opcional para despliegues institucionales
- Guía de despliegue en nube (`cloud-deploy.md`)
- Matriz de criterios de aceptación (`acceptance-matrix.md`)

## Pendiente (prioridad sugerida)

### Datos

- Fuente DANE división político-administrativa enriquecida (nombres departamentales)
- SIVIGILA y otros indicadores INS
- Segunda fuente de mortalidad para contraste

### Analítica

- GeoJSON municipal completo en mapa
- Drift multivariado y umbrales configurables
- Evaluación temporal por ventanas móviles documentada por indicador

### Producto

- Cliente OpenAPI generado automáticamente en frontend (sustituir stub)
- Autenticación institucional OAuth2 / SSO
- Export PDF nativo (server-side) además de impresión del navegador

### Operación

- Trazas OpenTelemetry
- CI verde en GitHub Actions
- Push de tags de release al remoto
