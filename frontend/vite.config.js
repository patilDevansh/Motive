import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In production FastAPI serves frontend/dist and the API from one origin.
// In development, Vite proxies the API paths to uvicorn so the app can keep
// using the same relative URLs (e.g. fetch("/recommend/intelligent")).
const API_TARGET = "http://127.0.0.1:8000";

export default defineConfig({
  plugins: [react()],
  base: "/",
  build: {
    outDir: "dist",
    emptyOutDir: true,
    assetsDir: "assets",
  },
  server: {
    port: 5173,
    proxy: {
      "/recommend": API_TARGET,
      "/health": API_TARGET,
    },
  },
});
