/**
 * OpenAPI-derived API paths. Regenerate with:
 * `cd backend && PYTHONPATH=src python scripts/export_openapi.py`
 * `cd frontend && npm run generate:api-types`
 */
export interface paths {
  "/health-indicators": {
    get: { responses: { 200: { content: { "application/json": unknown[] } } } };
  };
  "/predict-risk": {
    get: { responses: { 200: { content: { "application/json": Record<string, unknown> } } } };
  };
  "/data-drift": {
    get: { responses: { 200: { content: { "application/json": Record<string, unknown> } } } };
  };
  "/territorial-boundaries": {
    get: { responses: { 200: { content: { "application/json": Record<string, unknown> } } } };
  };
}

export type ApiPaths = keyof paths;
