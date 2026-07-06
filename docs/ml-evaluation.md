# Evaluación de modelos analíticos (MVP)

Documento de referencia para las fases 5 y 8 del roadmap.

## Modelos en serving

| Capacidad | Versión | Método | Evaluación |
|-----------|---------|--------|------------|
| **Predicción de brotes (principal)** | `randomforest-outbreak-v1.0.0` | Random Forest (15 features) + SHAP TreeExplainer | Validación temporal train ≤2020 / test ≥2021 |
| Predicción de brotes (fallback) | `outbreak-multivariate-v1.0.0` | Score multivariado rule-based | Contribuciones determinísticas |
| Riesgo territorial (contexto) | `mortality-relative-v1.0.0` | Score relativo vs mediana nacional | Descomposición rule-based |
| Riesgo territorial (promovido) | `ridge-mortality-risk-v1.0.0` | Ridge sobre panel mortalidad | SHAP LinearExplainer |
| Anomalías | `outbreak-cases-median-v1.0.0` | Ratio casos dengue vs mediana del periodo | Umbrales 1.5 / 2.0 |
| Tendencias | `prophet-annual-v1.0.0` o `linear-extrapolation-v1.0.0` | Prophet / fallback sobre series curadas | Panel multi-periodo |
| Insights | `composite-narrative-v1.0.0` | Plantillas determinísticas | Revisión humana obligatoria |

## Nivel intermedio (concurso)

| Criterio | Cumplimiento |
|----------|--------------|
| Conjuntos datos.gov.co | 4–5 (SIVIGILA, vacunación, PM2.5, mortalidad/ acceso) |
| Variables ML brotes | **15** (`OUTBREAK_ML_FEATURE_NAMES`) — ver [`data-dictionary.md`](data-dictionary.md) |
| Algoritmo | **RandomForestClassifier** (class_weight balanced) |
| Validación | Split temporal + métricas F1 / recall / ROC-AUC |
| Explicabilidad | **SHAP TreeExplainer** en serving |
| Integración multifuente | Ingesta municipal + resolver de datasets |

## Ciclo entrenar → promover → rollback (brotes)

```bash
cd backend
PYTHONPATH=src python ml/train_outbreak_experiment.py --from-db
PYTHONPATH=src python -m modules.outbreak_prediction.interfaces.ml_cli promote randomforest-outbreak-v1.0.0
PYTHONPATH=src python -m modules.outbreak_prediction.interfaces.ml_cli status
PYTHONPATH=src python -m modules.outbreak_prediction.interfaces.ml_cli rollback
```

## Ciclo entrenar → promover → rollback (riesgo territorial)

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
PYTHONPATH=src DATABASE_URL=... python ml/evaluate_temporal.py --from-db
```

Artefactos en `backend/ml/artifacts/`; promoción de brotes en `promoted-outbreak.json`; promoción de riesgo en `promoted.json`.

## Prophet

- Se activa con **≥ 3** observaciones anuales.
- Si Prophet no está disponible en el entorno, el servicio usa extrapolación lineal.
- Los intervalos de incertidumbre no se exponen en la API del MVP.

## Explicabilidad

- **Modo rule-based (fallback brotes):** `feature_contributions` determinísticas.
- **Modo promovido brotes:** contribuciones **SHAP TreeExplainer** sobre Random Forest.
- **Modo promovido riesgo:** contribuciones SHAP sobre Ridge.
- Correlación histórica **no implica causalidad**.

## Sesgos y límites

- Cobertura parcial de territorios según publicación en datos.gov.co.
- Validación epidemiológica externa no incluida en el software.
- El modelo Ridge replica la lógica relativa del MVP; no sustituye revisión experta.

## Próximos pasos

1. Monitoreo de drift multivariado y umbrales configurables.
2. Registro de experimentos con metadatos extendidos (semillas, datasets versionados).
3. Evaluación por ventanas móviles documentada por indicador.
