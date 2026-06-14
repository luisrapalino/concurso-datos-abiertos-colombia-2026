# Roadmap post-MVP

Extensiones sugeridas tras el hito institucional inicial.

## Datos

- Ingestión automática programada (cron/worker)
- Fuente DANE división político-administrativa
- SIVIGILA y otros indicadores INS
- Validación cruzada de códigos territoriales

## Analítica

- SHAP en serving para modelos entrenados promovidos
- Evaluación temporal cruzada documentada por indicador
- Análisis de sesgo por departamento / estrato

## Producto

- GeoJSON municipal completo en mapa
- Cliente OpenAPI generado en frontend
- Autenticación institucional (OAuth2 / SSO)
- Exportación PDF de informes territoriales

## Operación

- Trazas OpenTelemetry
- Alertas de drift automatizadas
- Backups Postgres programados + prueba de restauración trimestral
- Despliegue en nube con secretos gestionados
