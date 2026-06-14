import { defineConfig } from "vitest/config";

// Standalone Vitest config — the router tests are pure (node env, no DOM, no React plugin), which
// keeps this independent of vite.config.ts and free of the dual-vite plugin type conflict.
export default defineConfig({
  test: {
    environment: "node",
    include: ["src/**/*.{test,spec}.{ts,tsx}"],
  },
});
