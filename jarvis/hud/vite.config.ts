import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The HUD is a read-only consumer of the dev_graph (ADR-010). In dev, /api proxies to the
// FastAPI bridge so the browser hits one origin (no CORS); graph.json is served statically from
// public/. In prod the bridge mounts the built dist (Stage 5) — same single URL.
// Test config lives in vitest.config.ts (no plugins → avoids the dual-vite type clash).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (p) => p.replace(/^\/api/, ""),
      },
    },
  },
});
