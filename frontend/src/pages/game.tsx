import "vite/modulepreload-polyfill";

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { QueryClientProvider } from "react-query";
import "../index.css";
import "../Game.css";

import Game from "../components/game/Game";
import { queryClient } from "@/lib/queryClient";
import { ThemeProvider } from "@/stores/ThemeContext";

createRoot(document.getElementById("game")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <Game />
      </ThemeProvider>
    </QueryClientProvider>
  </StrictMode>,
);
