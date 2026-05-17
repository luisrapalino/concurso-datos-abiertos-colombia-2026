# Ciclo de vida de sistemas de aprendizaje automático (CRISP-ML(Q))

**Plataforma de Inteligencia Epidemiológica Territorial**

Este documento describe la metodología de ciclo de vida del componente de inteligencia artificial y analítica predictiva del proyecto, siguiendo una adaptación de **CRISP-ML** con énfasis en **calidad y gobernanza (CRISP-ML(Q))**. Su propósito es alinear el desarrollo, la validación, el despliegue y el mantenimiento con prácticas reconocidas en ingeniería de machine learning y con los principios arquitectónicos definidos en `AGENTS.md` (Clean Architecture, DDD, modelos como infraestructura analítica, IA explicable).

**Alcance.** Cubre los flujos desde la comprensión del negocio y los datos hasta el monitoreo en operación, incluyendo criterios de calidad, trazabilidad y auditabilidad. No sustituye políticas institucionales externas ni lineamientos legales específicos de cada fuente de datos; actúa como marco de referencia técnico del producto.

**Audiencia.** Equipos de datos, ingeniería de software, salud pública y gobierno de datos que intervengan en diseño, implementación o evaluación del sistema.

---

## 1. Business and Data Understanding

### 1.1 Problema

La toma de decisiones en salud pública territorial requiere síntesis oportuna de información histórica y actual, integración de señales geográficas y temporales, y apoyo analítico que sea **interpretable y auditable**. Sin un marco explícito de ciclo de vida, los modelos de machine learning pueden degradar la confianza institucional: predicciones difíciles de explicar, datos inconsistentes entre versiones y desalineación entre lo que el negocio necesita y lo que el sistema optimiza.

La plataforma aborda este vacío al combinar **datos abiertos**, **indicadores territoriales**, **detección de anomalías**, **pronósticos** e **insights explicables**, sin pretender reemplazar el juicio humano ni operar como caja negra.

### 1.2 Objetivos

**Objetivos de negocio (orientativos).**

- Apoyar la priorización territorial mediante **scoring de riesgo** y clasificación coherente con el dominio epidemiológico.
- Anticipar tendencias relevantes mediante **análisis temporal y predicciones** acotadas a ventanas y supuestos documentados.
- Detectar comportamientos atípicos que motiven **revisión analítica** (alertas territoriales), no acciones automáticas críticas sin validación humana.
- Mejorar la **legibilidad institucional** de los resultados mediante narrativas e insights interpretables.

**Objetivos técnicos alineados con el proyecto.**

- Reproducibilidad de pipelines y trazabilidad de datos, features y artefactos de modelo.
- Modularidad por **bounded contexts**: vigilancia epidemiológica, riesgo territorial, motor de predicción, detección de anomalías, generación de insights y núcleo compartido.
- Cumplimiento de **API First** y contratos versionados (`/api/v1`, OpenAPI).

### 1.3 Stakeholders

| Rol | Interés principal |
|-----|---------------------|
| **Tomadores de decisión en salud pública** | Utilidad territorial, claridad de supuestos, trazabilidad de recomendaciones analíticas. |
| **Analistas y epidemiología** | Calidad de datos, definición de indicadores, validación de resultados y sesgos. |
| **Ingeniería de datos y ML** | Pipelines reproducibles, versionado, evaluación y despliegue controlado. |
| **Ingeniería de producto / software** | Integración con dominio y aplicación, separación modelo–negocio, observabilidad. |
| **Gobierno de datos y cumplimiento** | Licencias de fuentes, retención, minimización y documentación de proveniencia. |
| **Ciudadanía e instituciones de datos abiertos** | Transparencia del uso de datos públicos y explicabilidad de alto nivel. |

### 1.4 Impacto esperado

- **Operativo:** reducción del esfuerzo manual de consolidación y exploración repetitiva mediante vistas, indicadores y alertas asistidas.
- **Analítico:** homogeneización de criterios de riesgo y de detección de anomalías en el tiempo, con registro de versiones y métricas.
- **Institucional:** mayor confianza cuando las predicciones y alertas van acompañadas de **explicaciones** y de **límites de uso** explícitos (el sistema no sustituye protocolos clínicos ni decisiones políticas finales).
- **Riesgos mitigados:** uso opaco de modelos, dependencia de notebooks como sistema de producción, y desalineación entre entrenamiento y serving.

### 1.5 Datasets

Los conjuntos de datos deben documentarse como **activos versionados**, con metadatos mínimos:

- **Proveniencia:** fuente, fecha de extracción, licencia y restricciones de uso.
- **Granularidad:** temporal (p. ej. semana, mes), territorial (división administrativa o equivalente acordada), unidad de análisis.
- **Diccionario de datos:** definición de campos, codificaciones y transformaciones aplicadas antes del modelado.
- **Calidad conocida:** tasas de missing, duplicados, inconsistencias cruzadas con catálogos territoriales.
- **Sensibilidad:** clasificación de datos personales o sensibles; políticas de anonimización o agregación cuando aplique.

Las fuentes iniciales se alinean con el contexto de **vigilancia epidemiológica** e **indicadores de salud** descritos en el dominio del proyecto; el inventario concreto de tablas y archivos se mantiene en catálogo de datos del repositorio o herramienta de gobierno elegida por el equipo.

---

## 2. Data Engineering

### 2.1 Ingestión

- **Contratos de entrada:** esquemas validados en la capa de interfaces; fallos explícitos ante violaciones de contrato.
- **Frecuencia y modos:** batch inicialmente (reproducible y auditable); evaluación de near–real-time solo si el negocio y la gobernanza de datos lo justifican.
- **Trazabilidad:** identificadores de corrida de ingestión, checksums o huellas cuando sea viable, y enlace a versiones de normalización.

### 2.2 Limpieza

- Reglas de limpieza **declarativas y reproducibles** (no lógica ad-hoc en capas de presentación).
- Tratamiento documentado de valores ausentes, outliers evidentes por error de captura vs. outliers legítimos del fenómeno.
- **Idempotencia** de pasos de limpieza para permitir re-ejecución sobre el mismo lote versionado.

### 2.3 Validación

- **Validaciones de integridad:** claves territoriales y temporales completas, rangos plausibles, coherencia entre tablas relacionadas.
- **Validaciones de negocio** acordadas con dominio (p. ej. exclusión mutua de categorías, sumas conservadas en agregaciones definidas).
- **Controles de regresión de datos:** comparación de distribuciones y conteos frente a línea base al incorporar nuevas fuentes o ventanas.

### 2.4 Transformación

- Normalización y estandarización alineadas con el **lenguaje ubicuo** del proyecto (mismos nombres en backend, APIs y documentación).
- Agregaciones territoriales y temporales explícitas en documentación de features.
- Separación entre **datos curados** para analítica y **vistas de consumo** para aplicación, evitando bifurcaciones no trazadas.

### 2.5 Feature engineering

- Catálogo de **features con definición, fórmula, ventana temporal y unidad**.
- Evitar fuga de información temporal (data leakage): partición estricta por tiempo cuando el caso de uso sea pronóstico.
- Versionado del conjunto de features (`feature set`) junto al dataset y al modelo que lo consume.
- Features derivadas de políticas sensibles (p. ej. variables proxy de grupos protegidos) sujetas a revisión ética y técnica antes de producción.

---

## 3. Modeling

### 3.1 Modelos seleccionados (marco de referencia)

El stack de referencia del proyecto incluye herramientas para modelos tabulares, series temporales y explicación post-hoc, entre ellas: **scikit-learn**, **XGBoost**, **Prophet** y **SHAP**, sobre **Python 3.12+**. La elección concreta por caso de uso (riesgo territorial, anomalías, tendencias) se documenta en la ficha de modelo correspondiente.

### 3.2 Justificación

Los criterios de selección combinan:

- **Capacidad predictiva o de ranking** acorde a métricas acordadas con el negocio.
- **Estabilidad** ante variaciones razonables de datos y ventanas temporales.
- **Costo operativo:** latencia de inferencia, memoria y complejidad de despliegue.
- **Alineación con gobernanza:** preferencia por modelos cuya conducta pueda inspeccionarse y explicarse a nivel agregado y, cuando sea necesario, local.

Los modelos que no aporten ventaja clara sobre baselines simples documentados no deben avanzar a producción.

### 3.3 Interpretabilidad

- **Modelos intrínsecamente interpretables** cuando cubran el rendimiento requerido (p. ej. modelos lineales o basados en reglas) como línea de comparación obligatoria.
- **Explicación post-hoc** (p. ej. SHAP) para modelos más expresivos, con advertencias sobre correlación de features y límites de causalidad.
- Toda predicción expuesta a usuarios institucionales debe poder asociarse a **narrativa analítica** o resumen de drivers principales, sin confundir correlación con causalidad.

### 3.4 Pipelines

- Pipelines de entrenamiento e inferencia **separados** de notebooks de exploración; los notebooks no son sistema de producción.
- Los artefactos de ML se tratan como **infraestructura analítica**: ensamblado, serialización y carga acotados a la capa de infraestructura, sin acoplar el dominio a frameworks de ML.
- **Reproducibilidad:** semillas donde aplique, versiones de dependencias fijadas (p. ej. imágenes Docker o archivos de lock), y registro de commits y parámetros de entrenamiento.

---

## 4. Evaluation

### 4.1 Métricas

Las métricas se definen **por caso de uso** y se acuerdan antes del ajuste fino del modelo:

- **Clasificación / ranking:** AUC-PR, AUC-ROC, Brier score, métricas a umbral fijo documentado; en desbalance severo, priorizar métricas sensibles a la clase minoritaria.
- **Regresión y pronóstico:** MAE, RMSE, MAPE (con precaución en ceros), intervalos de predicción cuando el negocio requiera expresión de incertidumbre.
- **Detección de anomalías:** precisión@k, tiempo hasta detección, o tasas de alerta acordadas con capacidad de revisión humana.
- **Métricas de negocio proxy:** costo asociado a falsos positivos vs. falsos negativos cuando se pueda cuantificar con stakeholders.

### 4.2 Validación

- **Particionado:** preferencia por validación temporal (walk-forward) para tareas de pronóstico; validación cruzada clásica solo cuando no rompa la estructura temporal.
- **Conjuntos holdout** reservados y no utilizados para decisiones iterativas de ingeniería de features para evitar optimismo de evaluación.
- **Pruebas de estrés de datos:** rendimiento bajo perturbaciones controladas (ruido, missing, retraso de publicación de datos).
- **Checklist de despliegue:** criterios mínimos de calidad de datos de entrada, límites de drift aceptables en validación previa al release.

### 4.3 Sesgos

- Análisis de **equidad territorial y demográfica** cuando existan variables o proxies que puedan introducir discriminación o refuerzo de desigualdades históricas en los datos.
- Evaluación por **subgrupos** (p. ej. regiones con baja densidad de datos) y documentación de degradación de métricas.
- Política explícita de **no uso** o restricción de variables sensibles, alineada con gobierno de datos y normativa aplicable.

### 4.4 Explicabilidad

- Diferenciar **explicación del modelo** (drivers de la predicción) de **explicación del sistema** (qué datos, qué versión, qué supuestos).
- Material de comunicación para no técnicos: lenguaje de dominio, visualizaciones coherentes con el frontend, y advertencias sobre incertidumbre.
- Registro de explicaciones representativas en evaluación para revisión por epidemiología o analistas antes de ampliar despliegue.

---

## 5. Deployment

### 5.1 Arquitectura

- **Monolito modular** inicial con límites claros entre dominio, aplicación e infraestructura, según `AGENTS.md`.
- Exposición de capacidades analíticas mediante **API REST versionada** (`/api/v1`), con OpenAPI como contrato.
- Endpoints orientativos del producto: predicción de riesgo, anomalías, tendencias territoriales, insights e indicadores de salud; el despliegue debe permitir **activación gradual** y **feature flags** cuando la complejidad operativa lo exija.

### 5.2 Serving

- Separación entre **entrenamiento offline** (o batch programado) y **inferencia online** o por solicitud, con tiempos de respuesta acordados.
- Contratos de request/response tipados (p. ej. Pydantic en FastAPI) y validación en borde.
- Estrategia de **carga de modelos** (arranque, caché, warm-up) documentada; evitar bloqueos largos en el hilo de atención de peticiones sin diseño explícito.

### 5.3 Reproducibilidad

- Versionado conjunto de: **código**, **datos o snapshot**, **features**, **hiperparámetros**, **imagen de entorno** y **artefacto de modelo**.
- Registro de experimentos (herramienta interna o MLflow u otra) alineado con trazabilidad exigida por auditoría.
- Política de **rollback** de modelo ante degradación de métricas o incidentes de datos.

### 5.4 Dockerización

- **Docker** y **Docker Compose** como base para entornos reproducibles de desarrollo, prueba y despliegue.
- Imágenes con capas minimizadas, usuario no root cuando sea posible, y variables de entorno para secretos (nunca credenciales en imagen).
- **PostgreSQL** como almacén relacional de referencia; migraciones y esquemas versionados según prácticas del backend.

---

## 6. Monitoring and Maintenance

### 6.1 Calidad de datos

- Monitores de **completitud, frescura, volumen y distribución** de variables críticas de entrada respecto a líneas base por fuente y por ventana temporal.
- Alertas ante rupturas de contrato de esquema o caídas de ingestión.
- Revisión periódica de catálogos territoriales y cambios administrativos que afecten joins.

### 6.2 Drift

- **Data drift:** desviación de distribución de inputs respecto al periodo de entrenamiento.
- **Concept drift:** deterioro sostenido de métricas de negocio o proxy en holdout operacional o en etiquetas tardías cuando existan.
- Plan de **re-entrenamiento o recalibración** con umbrales y responsables definidos; evitar reentrenamiento ciego sin diagnóstico de causa.

### 6.3 Monitoreo

- **Técnico:** latencia, tasas de error, uso de CPU/memoria, colas de trabajos batch.
- **Analítico:** distribución de scores, tasas de alerta, calibración de probabilidades en el tiempo.
- **Integración con insights:** registro de explicaciones solicitadas y feedback cualitativo de usuarios cuando se instrumente.

### 6.4 Mantenimiento futuro

- **Deuda de datos y modelo:** registro de limitaciones conocidas y trabajo planificado.
- **Retiro de modelos** (`sunsetting`) con periodo de convivencia de versiones y comunicación a consumidores de API.
- **Actualización de documentación** (este documento, fichas de modelo y catálogo de datos) como parte del Definition of Done de cada release relevante.
- Revisión anual o por hito mayor del marco CRISP-ML(Q) frente a regulación, nuevas fuentes o cambios de alcance territorial.

---

## Metodología de desarrollo y calidad (transversal)

- **Fases iterativas:** cada incremento debe poder cerrar un ciclo mínimo entendimiento → datos → modelo → evaluación → despliegue → monitoreo, aunque sea en alcance reducido (vertical slice).
- **Definition of Ready para modelado:** dataset versionado, feature set documentado, métricas acordadas y línea base definida.
- **Definition of Done para producción:** evaluación en conjunto de validación temporal, prueba de contrato de API, runbook de rollback y tablero mínimo de monitoreo activo.
- **Seguridad y privacidad:** principio de mínimo privilegio en accesos a datos; logs sin datos sensibles innecesarios.
- **Alineación DDD:** reglas de negocio en dominio/aplicación; modelos como infraestructura sustituible que cumple contratos del caso de uso.

---

## Control de documento

| Campo | Valor |
|-------|--------|
| **Identificador** | CRISP-ML(Q) – Plataforma de Inteligencia Epidemiológica Territorial |
| **Versión** | 1.0 |
| **Referencia normativa interna** | `AGENTS.md` (arquitectura, bounded contexts, reglas ML y API) |

*Fin del documento.*
