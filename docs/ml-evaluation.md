# Evaluación de modelos analíticos (MVP)

Documento de referencia para las fases 5 y 8 del roadmap.

## Modelos en serving

| Capacidad | Versión | Método | Evaluación |
|-----------|---------|--------|------------|
| Riesgo territorial | `mortality-relative-v1.0.0` | Score relativo vs mediana nacional | Auditable por descomposición de contribuciones |
| Anomalías | `mortality-median-v1.0.0` | Ratio vs mediana del periodo | Umbrales 1.5 / 2.0 revisables manualmente |
| Tendencias | `prophet-annual-v1.0.0` o `linear-extrapolation-v1.0.0` | Prophet con fallback lineal | Validación temporal pendiente de panel multi-año |
| Insights | `composite-narrative-v1.0.0` | Plantillas determinísticas | Revisión humana obligatoria |

## Prophet

- Se activa con **≥ 3** observaciones anuales.
- Si Prophet no está disponible en el entorno, el servicio usa extrapolación lineal.
- Los intervalos de incertidumbre no se exponen en la API del MVP.

## Explicabilidad

- El riesgo relativo expone `feature_contributions` con descomposición rule-based.
- SHAP se reserva para modelos entrenados offline (`backend/ml/train_mortality_experiment.py`).

## Sesgos y límites

- Cobertura parcial de territorios según publicación en datos.gov.co.
- Correlación histórica **no implica causalidad**.
- Validación epidemiológica externa no incluida en el software.

## Próximos pasos post-MVP

1. Ingestión multi-año y evaluación temporal cruzada.
2. Promoción de modelos entrenados con rollback documentado.
3. Monitoreo de drift en `ingestion_runs` y distribución de scores.
