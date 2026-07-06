# Diccionario de datos — modelo de brotes

Panel de entrenamiento e inferencia: **municipio × semana epidemiológica × dengue (SIVIGILA 210)**.

Implementación: `backend/src/modules/outbreak_prediction/domain/feature_engineering.py` (`OUTBREAK_ML_FEATURE_NAMES`).

## Identificadores

| Campo | Formato | Ejemplo | Fuente |
|-------|---------|---------|--------|
| `territorial_code` | DANE 5 dígitos | `05001` | DIVIPOLA |
| `period` | `YYYY-Www` | `2020-W33` | SIVIGILA |
| `event_code` | Código SIVIGILA | `210` | Dengue |

## Variables de entrada (15 features)

| # | Variable | Tipo | Descripción |
|---|----------|------|-------------|
| 1 | `log_observed_cases` | float | log(1 + casos observados) |
| 2 | `log_baseline_cases` | float | log(1 + mediana nacional del periodo) |
| 3 | `cases_vs_median` | float | Casos / mediana |
| 4 | `log_previous_week_cases` | float | log(1 + casos semana anterior) |
| 5 | `week_over_week_ratio` | float | Casos actuales / semana anterior |
| 6 | `vaccination_coverage_pct` | float | Cobertura DPT-HepB-Hib (%) |
| 7 | `vaccination_gap` | float | max(0, 100 − cobertura) |
| 8 | `health_access_pct` | float | Partos institucionales (%) |
| 9 | `health_access_gap` | float | max(0, 100 − acceso) |
| 10 | `pm25_ug_m3` | float | PM2.5 promedio anual (µg/m³) |
| 11 | `epidemiological_week_sin` | float | Componente seno estacional |
| 12 | `epidemiological_week_cos` | float | Componente coseno estacional |
| 13 | `cases_above_baseline` | binary | 1 si ratio ≥ 1.0 |
| 14 | `accelerated_growth` | binary | 1 si WoW ratio ≥ 1.5 |
| 15 | `territorial_risk_proxy` | float | ratio × gap_vac × (PM2.5/25) |

## Etiqueta de entrenamiento

| Variable | Definición |
|----------|------------|
| `outbreak_label` | 1 si ratio ≥ 1.5 o crecimiento semanal ≥ 1.5 |

## Defaults para valores ausentes

| Variable | Default |
|----------|---------|
| `vaccination_coverage_pct` | 85.0 |
| `health_access_pct` | 90.0 |
| `pm25_ug_m3` | 15.0 |

## Salida del modelo

| Campo | Descripción |
|-------|-------------|
| `outbreak_probability` | Probabilidad 0–100 (Random Forest) |
| `classification` | low / medium / high / critical |
| `feature_contributions` | Contribuciones SHAP por variable |

Fuentes abiertas: ver [`data-sources.md`](data-sources.md).
