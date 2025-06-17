import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "path";
import tailwindcss from "@tailwindcss/vite";

// https://vite.dev/config/
export default defineConfig({
  resolve: {
    alias: {
      "@": resolve("./src"),
      "@shared": resolve("./src/shared"),
      "@components": resolve("./src/components"),
      "@pages": resolve("./src/pages"),
    },
  },
  plugins: [react(), tailwindcss()],
  base: "/static/",
  server: {
    // port: 5173,          // 5173 is default port
    // host: "localhost",   // localhost is default host
  },
  build: {
    manifest: "manifest.json",
    outDir: resolve("./assets"),
    rollupOptions: {
      input: {
        home: resolve("./src/pages/home/index.tsx"),
      },
    },
  },
});
