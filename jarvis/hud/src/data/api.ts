// api.ts — one place that knows where the bridge lives.
//   • dev:  the app is served by Vite (:5173); "/api" is proxied to the bridge (:8000), no CORS.
//   • prod: the app is served BY the bridge (dist mounted on :8000); calls go same-origin to "/".
// graph.json is always relative (public/ in dev, dist root in prod).
export const API_BASE = import.meta.env.DEV ? "/api" : "";
export const GRAPH_JSON_URL = "graph.json";
