# Alineación con el reto del concurso

Documento de trazabilidad entre el enunciado del **Concurso de Datos Abiertos Colombia 2026** y la implementación de la plataforma.

**Nivel de complejidad objetivo:** **Intermedio**

## Equipo (ID 200)

| Campo | Valor |
|-------|--------|
| **ID equipo** | 200 |
| **Líder** | luisrapalino88@gmail.com |
| **Participante 2** | Rapalinorokate@gmail.com |
| **Validación registro equipo** | CUMPLE |
| **Validación registro de reto** | Reto registrado |
| **Reto** | Salud y Bienestar — desarrollar modelos de IA para predecir brotes de enfermedades transmisibles usando datos de salud pública, vacunación y condiciones ambientales |

## Mapeo: plantilla sugerida → este repositorio

La plantilla del concurso es orientativa. Este proyecto **no duplica carpetas**; la evidencia vive en la estructura existente:

| Sugerencia concurso | Ubicación en este repo |
|---------------------|------------------------|
| README / ficha técnica | [`README.md`](../README.md) |
| LICENSE | [`LICENSE`](../LICENSE) |
| requirements.txt | [`backend/requirements.txt`](../backend/requirements.txt) + [`requirements-ml.txt`](../backend/requirements-ml.txt) |
| docs/architecture | [`architecture.md`](architecture.md) |
| docs/data_dictionary | [`data-dictionary.md`](data-dictionary.md) |
| docs/marco_metodologico | [`crisp-ml.md`](crisp-ml.md) |
| docs/fuentes_datos | [`data-sources.md`](data-sources.md) |
| docs/validación | [`ml-evaluation.md`](ml-evaluation.md) |
| data/ (raw → output) | PostgreSQL curado + [`backend/data/`](../backend/data/) (DIVIPOLA) |
| src/ (ML modular) | [`backend/src/modules/outbreak_prediction/`](../backend/src/modules/outbreak_prediction/) |
| models/ | [`backend/ml/artifacts/`](../backend/ml/artifacts/) |
| pipelines/ | [`backend/ml/train_outbreak_experiment.py`](../backend/ml/train_outbreak_experiment.py) |
| tests/ | [`backend/tests/`](../backend/tests/) |
| CI | [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) |
| RECURSOS/ (presentación) | [`RECURSOS/`](../RECURSOS/) |
| Demo / reportes | Frontend [`/brotes`](../frontend/src/app/brotes/) + API OpenAPI |

## Enunciado del reto

> Desarrollar modelos de IA para predecir brotes de enfermedades transmisibles usando datos de salud pública, vacunación y condiciones ambientales.

**Datos sugeridos:** morbilidad, coberturas de vacunación, calidad del aire, acceso a servicios de salud.

**Impacto:** prevención y respuesta temprana del sistema de salud.

## Cómo responde la plataforma

| Requisito del reto | Implementación | Fuente abierta |
|--------------------|----------------|----------------|
| Morbilidad transmisible | Casos semanales SIVIGILA (dengue + 5 eventos adicionales) | [4hyg-wa9d](https://www.datos.gov.co/resource/4hyg-wa9d.json) |
| Vacunación | Cobertura **DPT-HepB-Hib pentavalente** (expandida a municipio) | [6i25-2hdt](https://www.datos.gov.co/resource/6i25-2hdt.json) |
| Calidad del aire | **PM2.5** promedio anual municipal (fallback SISAIRE) | [kekd-7v7h](https://www.datos.gov.co/resource/kekd-7v7h.json) / [yspz-pxxn](https://www.datos.gov.co/resource/yspz-pxxn.json) |
| Acceso a salud | **Partos institucionales** como proxy municipal | [4e4i-ua65](https://www.datos.gov.co/resource/4e4i-ua65.json) |
| Modelo de IA explicable | **`randomforest-outbreak-v1.0.0`** — Random Forest + SHAP | `GET /api/v1/outbreak-predictions` |
| Validación temporal | Train ≤2020, test ≥2021 (métricas en artefacto JSON) | `backend/ml/train_outbreak_experiment.py --from-db` |
| Respuesta temprana | Alertas + mapa de señales | `/anomalies`, `/outbreak-map`, UI `/brotes` |

## Evidencia nivel intermedio

| Criterio concurso | Evidencia en el proyecto |
|-------------------|--------------------------|
| 3–10 conjuntos datos.gov.co | 4–5 conjuntos analíticos + DIVIPOLA |
| 10–20 variables | **15 features ML** en `OUTBREAK_ML_FEATURE_NAMES` |
| ML avanzado (Random Forest) | `RandomForestClassifier` entrenado offline |
| Integración multifuente | Ingesta `ingest-sync-municipal`, resolver PM2.5 |
| Validación de modelos | Split temporal + F1 / recall / ROC-AUC en metadata |
| Insights accionables | Alertas, mapa, informe territorial, narrativa explicable |
| Interpretabilidad | SHAP TreeExplainer + fallback rule-based auditable |

## Definición operativa de “brote”

- **Unidad:** municipio + semana epidemiológica (`YYYY-Www`).
- **Evento inicial:** dengue (código SIVIGILA `210`).
- **Etiqueta de entrenamiento:** ratio casos/mediana ≥ 1.5 o crecimiento semanal ≥ 1.5.
- **Inferencia:** probabilidad 0–100 del Random Forest promovido (fallback rule-based si no hay modelo activo).
- **Límite:** apoyo analítico con revisión humana obligatoria; no activación automática de emergencia.

## Ingestión de fuentes

Sincronización municipal inteligente (resolver de datasets, fallback PM2.5, trazabilidad en `ingestion_runs`):

```bash
./scripts/sync-open-data-batch.sh
```

Detalle por fuente en [`data-sources.md`](data-sources.md). Configura `SOCRATA_APP_TOKEN` para consumo responsable de la API SODA.

## Ciclo ML de brotes

```bash
cd backend
PYTHONPATH=src python ml/train_outbreak_experiment.py --from-db
PYTHONPATH=src python -m modules.outbreak_prediction.interfaces.ml_cli promote randomforest-outbreak-v1.0.0
```

Ver [`ml-evaluation.md`](ml-evaluation.md) y [`data-dictionary.md`](data-dictionary.md).

## Reproducir resultados (guía para evaluadores)

```bash
# 1. Levantar plataforma
cp .env.example .env
docker compose up --build -d

# 2. Sincronizar datos abiertos (requiere SOCRATA_APP_TOKEN en .env)
./scripts/sync-open-data-batch.sh

# 3. Entrenar y promover modelo de brotes
docker compose exec api python ml/train_outbreak_experiment.py --from-db
docker compose exec api python -m modules.outbreak_prediction.interfaces.ml_cli promote randomforest-outbreak-v1.0.0

# 4. Verificar predicción
curl "http://localhost:8000/api/v1/outbreak-predictions?territorial_code=05001&period=2020-W33&event_code=210"
```

## API principal del reto

- `GET /api/v1/outbreak-alerts?period=2022-W33&limit=10` — ranking territorial
- `GET /api/v1/outbreak-predictions?territorial_code=05001&period=2020-W33`
- `GET /api/v1/outbreak-map?period=2020-W33&limit=100`
- `GET /api/v1/anomalies` (por defecto sobre casos de dengue)

## Límites honestos

- Cobertura de calidad del aire limitada a municipios con estaciones reportadas.
- Vacunación disponible a nivel departamental; se replica por municipio del mismo departamento.
- Validación epidemiológica externa no incluida en el software.
- El fallback rule-based permanece disponible vía rollback del modelo promovido.
