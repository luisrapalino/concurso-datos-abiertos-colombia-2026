# Evaluación de modelos analíticos (MVP)

Documento de referencia para las fases 5 y 8 del roadmap.

## Modelos en serving

| Capacidad | Versión | Método | Evaluación |
|-----------|---------|--------|------------|
| Riesgo territorial (default) | `mortality-relative-v1.0.0` | Score relativo vs mediana nacional | Descomposición rule-based |
| Riesgo territorial (promovido) | `ridge-mortality-risk-v1.0.0` | Ridge sobre panel `[observado, mediana, ratio]` | SHAP `LinearExplainer` en serving |
| Anomalías | `mortality-median-v1.0.0` | Ratio vs mediana del periodo | Umbrales 1.5 / 2.0 revisables manualmente |
| Tendencias | `prophet-annual-v1.0.0` o `linear-extrapolation-v1.0.0` | Prophet con fallback lineal | Panel multi-año 2018–2020 disponible |
| Insights | `composite-narrative-v1.0.0` | Plantillas determinísticas | Revisión humana obligatoria |

## Ciclo entrenar → promover → rollback

```bash
cd backend
PYTHONPATH=src python ml/train_mortality_experiment.py
PYTHONPATH=src python -m modules.territorial_risk.interfaces.ml_cli promote ridge-mortality-risk-v1.0.0
PYTHONPATH=src python -m modules.territorial_risk.interfaces.ml_cli status
PYTHONPATH=src python -m modules.territorial_risk.interfaces.ml_cli rollback
```

Entrenamiento desde PostgreSQL curado:

```bash
PYTHONPATH=src DATABASE_URL=... python ml/train_mortality_experiment.py --from-db
```

Artefactos en `backend/ml/artifacts/`; promoción en `promoted.json`.

## Prophet

- Se activa con **≥ 3** observaciones anuales.
- Si Prophet no está disponible en el entorno, el servicio usa extrapolación lineal.
- Los intervalos de incertidumbre no se exponen en la API del MVP.

## Explicabilidad

- **Modo rule-based:** `feature_contributions` con descomposición determinística.
- **Modo promovido:** contribuciones SHAP sobre el modelo Ridge activo.
- Correlación histórica **no implica causalidad**.

## Sesgos y límites

- Cobertura parcial de territorios según publicación en datos.gov.co.
- Validación epidemiológica externa no incluida en el software.
- El modelo Ridge replica la lógica relativa del MVP; no sustituye revisión experta.

## Próximos pasos

1. Evaluación temporal cruzada documentada por indicador.
2. Monitoreo de drift en scores y calidad de ingestión.
3. Registro de experimentos con metadatos extendidos (semillas, datasets versionados).
