# Alcance MVP — Vigilancia temprana de brotes

Documento breve de producto alineado al reto del **Concurso de Datos Abiertos Colombia 2026**.

## Objetivo

Entregar un **vertical slice** de predicción explicable de brotes de enfermedades transmisibles: datos abiertos multivariados en PostgreSQL, modelos interpretables vía API y trazabilidad hasta la fuente.

Ver [`concurso-alignment.md`](concurso-alignment.md) para la matriz requisito → implementación.

## Geografía

- **Nivel territorial:** municipio (código DANE de 5 dígitos).
- **Departamento:** derivable de los dos primeros dígitos del código municipal.
- **Cobertura:** según publicación en datos.gov.co; la UI comunica lagunas (p. ej. PM2.5 solo donde hay estación).

## Temporalidad

- **Morbilidad (SIVIGILA):** semana epidemiológica (`YYYY-Www`).
- **Vacunación, acceso, mortalidad contextual:** año calendario (`YYYY-01`).
- **Ventana inicial:** 2020 (último año con series completas en fuentes piloto).

## Fuentes prioritarias

| Prioridad | Fuente | Uso |
|-----------|--------|-----|
| 1 | SIVIGILA — vigilancia en salud pública (`4hyg-wa9d`) | Casos semanales de dengue |
| 2 | Coberturas vacunación departamental (`6i25-2hdt`) | Feature de protección (pentavalente) |
| 3 | Calidad del aire PM2.5 IDEAM (`yspz-pxxn`) | Feature ambiental |
| 4 | Indicadores INS mortalidad/morbilidad (`4e4i-ua65`) | Proxy acceso (partos institucionales) + contexto |
| 5 | DIVIPOLA DANE | Validación territorial |

## Significado operativo de “brote”

- **No** es confirmación clínica ni declaratoria automática de emergencia.
- **Sí** es una **señal territorial explicable** para priorizar revisión epidemiológica temprana, con versión de modelo y supuestos explícitos.

## Criterios de aceptación

1. Ingestión idempotente de las cuatro familias de datos (CLI + worker).
2. `GET /api/v1/outbreak-predictions` con probabilidad, clasificación y contribuciones por feature.
3. `GET /api/v1/outbreak-map` para exploración geográfica de señales.
4. `GET /api/v1/anomalies` sobre casos de dengue por defecto.
5. Frontend con página `/brotes`, alertas y documentación de linaje.
6. OpenAPI actualizado.

## Límites explícitos

- Un evento transmisible piloto (dengue); extensible a sarampión, tuberculosis, etc.
- Sin autenticación institucional en MVP.
- Sin validación epidemiológica externa incluida en el software.
