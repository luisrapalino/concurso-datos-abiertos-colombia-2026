# Demo institucional — Plataforma de Inteligencia Epidemiológica Territorial

Guión sugerido para presentación del MVP (15–20 minutos).

## Preparación

```bash
docker compose up --build -d
docker compose exec api python -m modules.epidemiological_surveillance.interfaces.scheduler --once
docker compose exec api python -m modules.territorial_risk.interfaces.ml_cli promote ridge-mortality-risk-v1.0.0
```

Abrir: http://localhost:3002 (o puerto configurado en override).

Filtros demo: territorio **05001** (Medellín), periodo **2020-01**.

## Recorrido

1. **Inicio** — explicar propósito: apoyo analítico, no decisión clínica automática.
2. **Frescura de datos** — badge en header; fuente INS / datos.gov.co.
3. **Indicadores** — tabla con valor observado e `ingested_at`.
4. **Riesgo** — score, clasificación, drivers y contribuciones SHAP (si modelo promovido).
5. **Anomalías** — alertas relativas a mediana del periodo.
6. **Tendencias** — histórico 2018–2020 + proyección Prophet.
7. **Insights** — narrativa con `system_context` y fuentes.
8. **Mapa** — municipios DIVIPOLA + contornos departamentales DANE.
9. **API** — `/docs` para trazabilidad OpenAPI.

## Mensajes clave de cierre

- Cobertura parcial según publicación en datos abiertos.
- Validación epidemiológica externa requerida antes de uso operativo.
- Modelos versionados con rollback documentado.

## Límites explícitos

Ver [`mvp-scope.md`](mvp-scope.md) y [`ml-evaluation.md`](ml-evaluation.md).
