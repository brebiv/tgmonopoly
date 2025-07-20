/// <reference types="vitest/config" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "path";
import tailwindcss from "@tailwindcss/vite";

// https://vite.dev/config/
import path from "node:path";
import { fileURLToPath } from "node:url";
import { storybookTest } from "@storybook/addon-vitest/vitest-plugin";
const dirname = typeof __dirname !== "undefined" ? __dirname : path.dirname(fileURLToPath(import.meta.url));

// More info at: https://storybook.js.org/docs/next/writing-tests/integrations/vitest-addon
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
    port: 5173, // 5173 is default port
    host: "localhost", // localhost is default host
    origin: "http://localhost:5173",
    strictPort: true,
  },
  build: {
    manifest: "manifest.json",
    outDir: resolve("./assets"),
    rollupOptions: {
      input: {
        home: resolve("./src/pages/home/index.tsx"),
        game: resolve("./src/pages/game/index.tsx"),
      },
    },
  },
  envDir: "../",
  test: {
    projects: [
      {
        extends: true,
        plugins: [
          // The plugin will run tests for the stories defined in your Storybook config
          // See options at: https://storybook.js.org/docs/next/writing-tests/integrations/vitest-addon#storybooktest
          storybookTest({
            configDir: path.join(dirname, ".storybook"),
          }),
        ],
        test: {
          name: "storybook",
          browser: {
            enabled: true,
            headless: true,
            provider: "playwright",
            instances: [
              {
                browser: "chromium",
              },
            ],
          },
          setupFiles: [".storybook/vitest.setup.ts"],
        },
      },
    ],
  },
});
