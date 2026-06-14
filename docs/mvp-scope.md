# Alcance MVP institucional

Documento breve de producto para la primera versión demostrable de la plataforma.

## Objetivo

Entregar un **vertical slice** de inteligencia epidemiológica territorial: datos abiertos curados en PostgreSQL, consultables vía API y trazables hasta su fuente.

## Geografía

- **Nivel territorial:** municipio (código DANE de 5 dígitos) como granularidad principal del primer dataset.
- **Departamento:** derivable de los dos primeros dígitos del código municipal.
- **Cobertura inicial:** datos publicados en el portal nacional; la UI debe comunicar lagunas o territorios sin registro.

## Temporalidad

- **Primer dataset:** indicadores **anuales** (año calendario).
- **Representación en API:** periodo `YYYY-01` (convención interna para series anuales).
- **Ventana inicial:** años disponibles en la fuente (último año publicado: **2020** al momento del MVP).

## Fuentes prioritarias (fase actual)

| Prioridad | Fuente | Uso en MVP |
|-----------|--------|------------|
| 1 | [Indicadores mortalidad y morbilidad](https://www.datos.gov.co/Salud-y-Protecci-n-Social/Indicadores-mortalidad-y-morbilidad-seg-n-departam/4e4i-ua65) (INS / datos.gov.co) | Primera ingestión real: `TASA DE MORTALIDAD GENERAL` |
| 2 | División político-administrativa DANE | Validación de códigos territoriales en ingestión (catálogo DIVIPOLA embebido) |
| 3 | SIVIGILA event-level | Ampliación post-MVP |

## Significado operativo de “riesgo”

- **No** es decisión clínica individual ni alerta automática vinculante.
- **Sí** es un **score territorial relativo** para priorizar revisión analítica humana, con versión de reglas/modelo y supuestos explícitos.
- Los endpoints analíticos (`predict-risk`, `anomalies`, `territorial-trends`, `insights`) operan sobre **datos curados** con trazabilidad y explicaciones acotadas.

## Criterios de aceptación del vertical slice

1. Un job/CLI de ingestión carga observaciones idempotentes en PostgreSQL.
2. Cada corrida queda registrada (`ingestion_runs`) con estado y conteo de registros.
3. `GET /api/v1/health-indicators` devuelve observaciones reales filtrables por territorio y periodo.
4. `GET /api/v1/data-freshness` expone la última ingestión exitosa.
5. `GET /api/v1/predict-risk` persiste scores auditables con contribuciones explicables.
6. OpenAPI refleja los campos `period`, `value` y metadatos de fuente.
7. Frontend cubre indicadores, riesgo, anomalías, tendencias, insights y mapa territorial.
8. Documentación de linaje en [`data-sources.md`](data-sources.md).

## Límites explícitos

- Sin autenticación institucional en MVP.
- Sin cobertura nacional garantizada en todos los indicadores.
- Sin validación epidemiológica externa incluida en el software.
- Prophet y experimentos SHAP offline complementan reglas MVP; ver [`ml-evaluation.md`](ml-evaluation.md).
