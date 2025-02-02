import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "path";
import path from "path";
import { TanStackRouterVite } from "@tanstack/router-plugin/vite";
// import { fileURLToPath } from "url";

// const __filename = fileURLToPath(import.meta.url);
// const __dirname = path.dirname(__filename);

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), TanStackRouterVite({ enableRouteGeneration: false })],
  base: "/static/",
  build: {
    manifest: "manifest.json",
    outDir: resolve("./assets"),
    rollupOptions: {
      input: {
        home: resolve("./src/pages/home.tsx"),
        game: resolve("./src/pages/game.tsx"),
        create_game: resolve("./src/pages/create_game.tsx"),
      },
    },
  },
  server: {
    origin: "http://localhost:5173", // Development server origin
    port: 5173, // Vite development server port
    strictPort: true, // Ensure the port is available
    hmr: {
      host: "localhost", // HMR host for Vite
      protocol: "ws", // WebSocket for HMR
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
});
