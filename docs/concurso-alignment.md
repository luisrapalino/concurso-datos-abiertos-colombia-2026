# Alineación con el reto del concurso

Documento de trazabilidad entre el enunciado del **Concurso de Datos Abiertos Colombia 2026** y la implementación de la plataforma.

## Enunciado del reto

> Desarrollar modelos de IA para predecir brotes de enfermedades transmisibles usando datos de salud pública, vacunación y condiciones ambientales.

**Datos sugeridos:** morbilidad, coberturas de vacunación, calidad del aire, acceso a servicios de salud.

**Impacto:** prevención y respuesta temprana del sistema de salud.

## Cómo responde la plataforma

| Requisito del reto | Implementación | Fuente abierta |
|--------------------|----------------|----------------|
| Morbilidad transmisible | Casos semanales de **dengue** (SIVIGILA) | [4hyg-wa9d](https://www.datos.gov.co/resource/4hyg-wa9d.json) |
| Vacunación | Cobertura **DPT-HepB-Hib pentavalente** (expandida a municipio) | [6i25-2hdt](https://www.datos.gov.co/resource/6i25-2hdt.json) |
| Calidad del aire | **PM2.5** promedio anual por estación → municipio | [yspz-pxxn](https://www.datos.gov.co/resource/yspz-pxxn.json) |
| Acceso a salud | **Partos institucionales** como proxy municipal | [4e4i-ua65](https://www.datos.gov.co/resource/4e4i-ua65.json) |
| Modelo de IA explicable | `outbreak-multivariate-v1.0.0` con contribuciones por feature | `GET /api/v1/outbreak-predictions` |
| Respuesta temprana | Alertas sobre casos vs mediana + mapa de señales | `/anomalies`, `/outbreak-map`, UI `/brotes` |

## Definición operativa de “brote”

- **Unidad:** municipio + semana epidemiológica (`YYYY-Www`).
- **Evento inicial:** dengue (código SIVIGILA `210`).
- **Señal:** probabilidad 0–100 compuesta por elevación de casos, crecimiento semanal, brechas de vacunación/acceso y exposición a PM2.5.
- **Límite:** apoyo analítico con revisión humana obligatoria; no activación automática de emergencia.

## Ingestión de fuentes

Sincronización incremental por lotes (año descendente, paginación de 1000 registros):

```bash
./scripts/sync-open-data-batch.sh
```

Detalle por fuente en [`data-sources.md`](data-sources.md).

## API principal del reto

- `GET /api/v1/outbreak-alerts?period=2022-W33&limit=10` — ranking territorial
- `GET /api/v1/outbreak-predictions?territorial_code=05001&period=2020-W33`
- `GET /api/v1/outbreak-map?period=2020-W33&limit=100`
- `GET /api/v1/anomalies` (por defecto sobre casos de dengue)

## Límites honestos

- Cobertura de calidad del aire limitada a municipios con estaciones reportadas en SISAIRE.
- Vacunación disponible a nivel departamental; se replica por municipio del mismo departamento.
- Validación epidemiológica externa no incluida en el software.
