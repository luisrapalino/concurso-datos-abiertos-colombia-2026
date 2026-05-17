# AGENTS.md

# Plataforma de Inteligencia Epidemiológica Territorial

## Project Overview

Este proyecto tiene como objetivo construir una plataforma de inteligencia epidemiológica territorial basada en datos abiertos e inteligencia artificial explicable para apoyar la toma de decisiones en salud pública.

La plataforma permitirá:

- analizar datos históricos de salud pública,
- calcular indicadores territoriales,
- detectar anomalías,
- generar predicciones,
- producir insights automáticos,
- y visualizar información epidemiológica de forma clara e interactiva.

El sistema estará diseñado como una solución:

- escalable,
- reproducible,
- modular,
- auditable,
- y alineada con principios de arquitectura limpia y Domain-Driven Design (DDD).

---

## Roadmap de implementación

El plan por fases hasta un producto mínimo institucional completo (datos, API, ML explicable, frontend y operación) está en [`docs/roadmap.md`](docs/roadmap.md).

---

# Objetivos Técnicos

## Funcionales

- Procesar datasets históricos de salud pública.
- Generar scoring de riesgo territorial.
- Detectar comportamientos atípicos.
- Realizar análisis temporal y predicciones.
- Exponer endpoints REST reutilizables.
- Visualizar datos geográficos y temporales.
- Generar explicaciones interpretables.

## No Funcionales

- Mantener alta mantenibilidad.
- Garantizar reproducibilidad.
- Facilitar escalabilidad.
- Mantener separación clara de responsabilidades.
- Garantizar trazabilidad de datos y modelos.
- Permitir auditabilidad del sistema.

---

# Stack Tecnológico

## Frontend

- Next.js
- TypeScript
- Tailwind CSS
- shadcn/ui
- Apache ECharts
- Leaflet
- Zustand
- Framer Motion

## Backend

- FastAPI
- Python 3.12+
- SQLAlchemy
- Pydantic

## Machine Learning

- Pandas
- NumPy
- Scikit-learn
- XGBoost
- Prophet
- SHAP

## Base de Datos

- PostgreSQL

## Infraestructura

- Docker
- Docker Compose

---

# Principios Arquitectónicos

El sistema debe seguir:

- Domain-Driven Design (DDD)
- Clean Architecture
- Separation of Concerns
- SOLID Principles
- Modular Monolith (inicialmente)
- API First
- Explainable AI

---

# Reglas Generales de Arquitectura

## Reglas Obligatorias

- La lógica de negocio NO debe vivir en controllers.
- La lógica de negocio NO debe vivir en componentes UI.
- La lógica de negocio NO debe vivir en notebooks.
- Toda regla de negocio debe pertenecer al dominio o aplicación.
- Los modelos de IA deben tratarse como infraestructura.
- El dominio nunca debe depender de infraestructura.
- Las entidades deben proteger sus invariantes.
- Los Value Objects deben ser inmutables.
- Las dependencias deben apuntar hacia adentro.
- Evitar lógica duplicada.
- Priorizar composición sobre herencia.
- Mantener alta cohesión y bajo acoplamiento.

---

# Bounded Contexts

## EpidemiologicalSurveillance

Responsable de:

- ingestión de datos,
- eventos epidemiológicos,
- normalización,
- indicadores de salud.

## TerritorialRisk

Responsable de:

- scoring territorial,
- cálculo de riesgo,
- clasificación territorial.

## PredictionEngine

Responsable de:

- forecasting,
- tendencias,
- predicciones temporales.

## AnomalyDetection

Responsable de:

- detección de anomalías,
- comportamiento atípico,
- alertas territoriales.

## InsightsGeneration

Responsable de:

- explicaciones automáticas,
- insights interpretables,
- narrativa analítica.

## SharedKernel

Responsable de:

- contratos compartidos,
- tipos comunes,
- utilidades transversales.

---

# Arquitectura Backend

El backend debe organizarse siguiendo:

- dominio,
- aplicación,
- infraestructura,
- interfaces.

## Estructura Esperada

backend/src/

- modules/
- shared/
- infrastructure/
- api/
- config/

Cada módulo debe contener:

- domain/
- application/
- infrastructure/
- interfaces/

---

# Reglas Backend

- Controllers únicamente orquestan requests/responses.
- Nunca acceder directamente a infraestructura desde controllers.
- Los casos de uso viven en application/.
- El dominio NO conoce frameworks.
- DTOs separados de entidades de dominio.
- Validaciones externas deben hacerse en interfaces.
- Reglas de negocio en domain/.
- Infraestructura implementa contratos del dominio.

---

# Arquitectura Frontend

El frontend debe ser:

- feature-driven,
- modular,
- orientado al dominio.

## Objetivos

- mantener reutilización,
- separar presentación y lógica,
- evitar componentes gigantes,
- mantener consistencia visual.

---

# Reglas Frontend

- Los componentes deben ser principalmente presentacionales.
- La lógica compleja debe vivir en hooks/services.
- Evitar lógica de negocio en páginas.
- Mantener tipado fuerte.
- Evitar duplicación de gráficos y mapas.
- Mantener consistencia visual usando DESIGN.md.
- Usar terminología del dominio.

---

# Arquitectura de Machine Learning

Los modelos ML deben considerarse infraestructura analítica.

## Objetivos

- reproducibilidad,
- interpretabilidad,
- trazabilidad,
- facilidad de entrenamiento.

## Ciclo de vida y calidad (CRISP-ML(Q))

El marco metodológico del ciclo de vida del ML (comprensión de negocio y datos, ingeniería de datos, modelado, evaluación, despliegue, monitoreo y mantenimiento), así como la estrategia de calidad y validación, está descrito en [`docs/crisp-ml.md`](docs/crisp-ml.md).

---

# Reglas ML

- Todos los modelos deben ser explicables.
- Evitar black-box innecesarios.
- Mantener pipelines reproducibles.
- Versionar datasets y modelos.
- Documentar features.
- Mantener separación entre entrenamiento y serving.
- Toda predicción debe poder explicarse.

---

# Reglas API

## Convenciones

- RESTful APIs
- Versionado vía /api/v1
- Responses consistentes
- DTOs explícitos
- OpenAPI obligatorio

## Endpoints Iniciales

- /predict-risk
- /anomalies
- /territorial-trends
- /insights
- /health-indicators

---

# Convenciones de Naming

## Entidades

Usar nombres explícitos del dominio.

Ejemplos:

- RiskScore
- TerritorialIndicator
- EpidemiologicalEvent
- PredictionWindow
- AnomalyAlert

## Evitar

- data
- item
- info
- object
- manager
- helper

---

# Ubiquitous Language

El lenguaje del dominio debe mantenerse consistente en:

- backend,
- frontend,
- documentación,
- APIs,
- modelos,
- bases de datos.

Todos los equipos y agentes IA deben respetar el mismo vocabulario.

---

# Reglas de Calidad

## Obligatorias

- Código tipado.
- Código modular.
- Funciones pequeñas.
- Responsabilidad única.
- Evitar acoplamiento innecesario.
- Evitar archivos gigantes.
- Priorizar legibilidad sobre complejidad.

---

# Reglas para Cursor y Agentes IA

## Instrucciones Obligatorias

- Preservar límites DDD.
- Nunca bypass application layer.
- No generar lógica duplicada.
- Reutilizar abstracciones existentes.
- Mantener consistencia de naming.
- No mezclar dominio con infraestructura.
- No mover lógica de negocio a controllers o UI.
- Priorizar código mantenible.
- Generar código fuertemente tipado.
- Mantener separación de responsabilidades.
- Mantener arquitectura modular.
- Respetar bounded contexts.
- No generar soluciones temporales o hacks.
- Mantener consistencia con DESIGN.md.

## Commits (git)

Al crear commits (solo cuando el usuario lo pida explícitamente), seguir la skill del proyecto [`.cursor/skills/atomic-commits/SKILL.md`](.cursor/skills/atomic-commits/SKILL.md):

- **Un commit = un propósito** (atómico, revertible, estado coherente).
- Dividir cambios mezclados (código, docs, infra, formato) en commits separados.
- Mensajes en **Conventional Commits** (`feat`, `fix`, `docs`, …); el cuerpo explica el *por qué*.
- No incluir secretos (`.env`, credenciales) ni commitear sin solicitud del usuario.

---

# No Objetivos

El proyecto NO busca:

- reemplazar decisiones humanas,
- usar IA como caja negra,
- construir un chatbot genérico,
- implementar microservicios prematuramente,
- priorizar complejidad innecesaria,
- sacrificar mantenibilidad por velocidad.

---

# Filosofía del Proyecto

La plataforma debe percibirse como:

- una herramienta institucional seria,
- un sistema analítico confiable,
- una solución escalable,
- y una plataforma de inteligencia pública basada en datos abiertos e IA explicable.
