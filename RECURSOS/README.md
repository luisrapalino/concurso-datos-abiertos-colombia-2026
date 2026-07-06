# Recursos visuales — Concurso Datos Abiertos 2026

Material de presentación del **Equipo ID 200** (nivel **Intermedio IA**).

**Reto:** Salud y Bienestar — predicción de brotes transmisibles con datos abiertos.

## Archivos a incluir

| Archivo | Descripción |
|---------|-------------|
| `Presentacion.pptx` | Presentación editable |
| `presentacion.pdf` | Versión PDF para evaluación |
| `portada.png` | Captura de la diapositiva principal |

## Contenido sugerido

1. Problema: predicción de brotes transmisibles con datos abiertos
2. Fuentes datos.gov.co integradas (ver [`docs/data-sources.md`](../docs/data-sources.md))
3. Arquitectura de la plataforma (ver [`docs/architecture.md`](../docs/architecture.md))
4. 15 variables del modelo (ver [`docs/data-dictionary.md`](../docs/data-dictionary.md))
5. Random Forest + SHAP — demo en `/brotes`
6. Validación temporal y limitaciones honestas
7. Demo en vivo: frontend + API

## Capturas útiles

- UI: http://localhost:3002/brotes (o puerto configurado)
- API: http://localhost:8000/docs
- Métricas del modelo: `backend/ml/artifacts/randomforest-outbreak-v1.0.0.json`
