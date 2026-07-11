# Recursos visuales — Concurso Datos Abiertos 2026

Material de presentación del **Equipo ID 200** (nivel **Intermedio IA**).

**Reto:** Salud y Bienestar — predicción de brotes transmisibles con datos abiertos.

## Archivos a incluir

| Archivo             | Descripción                                                            |
| ------------------- | ---------------------------------------------------------------------- |
| `Presentacion.pptx` | Presentación editable (8 diapositivas, lineamientos sustentación 2026) |
| `presentacion.pdf`  | Versión PDF para evaluación                                            |
| `portada.png`       | Captura de la diapositiva principal                                    |
| `screenshots/`      | Capturas de la demo en producción (brotes, mapa, landing)              |

Regenerar capturas desde la demo en Vercel:

```bash
cd frontend
E2E_BASE_URL=https://concurso-datos-abiertos-colombia-20.vercel.app npx playwright test e2e/capture-screenshots.spec.ts
```

Regenerar tras cambios en métricas del modelo o capturas:

```bash
docker compose run --rm --no-deps -v "$(pwd):/repo" --entrypoint sh api \
  -c "pip install python-pptx reportlab Pillow -q && python /repo/scripts/build-concurso-presentation.py"
```

## Estructura del pitch (10 min)

1. Portada — ID 200, nivel Intermedio, integrantes
2. Problema y objetivo
3. Datos abiertos — fuentes, variables, tratamiento
4. Solución e IA — Random Forest + SHAP
5. Resultados y demo — métricas + `/brotes`
6. Impacto — valor público y sostenibilidad
7. Repositorio — GitHub y documentación
8. Cierre — valor diferencial

## Demo en línea

| Recurso | URL |
|---------|-----|
| Plataforma | https://concurso-datos-abiertos-colombia-20.vercel.app/ |
| Radar de brotes | https://concurso-datos-abiertos-colombia-20.vercel.app/brotes |
| Mapa | https://concurso-datos-abiertos-colombia-20.vercel.app/mapa |
| API | https://epintel-api.onrender.com/docs |

## Capturas útiles

- UI en producción: https://concurso-datos-abiertos-colombia-20.vercel.app/brotes
- UI local: http://localhost:3002/brotes (o puerto configurado)
- API en producción: https://epintel-api.onrender.com/docs
- API local: http://localhost:8000/docs
- Métricas del modelo: `backend/ml/artifacts/randomforest-outbreak-v1.0.0.json`
