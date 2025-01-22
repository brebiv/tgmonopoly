import "vite/modulepreload-polyfill";

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { QueryClientProvider } from "react-query";
import "../index.css";
import "../Game.css";

import Game from "../components/game/Game";
import { queryClient } from "@/lib/queryClient";
import { ThemeProvider } from "@/stores/ThemeContext";
import { WebsocketContextProvider } from "@/stores/WebsocketContext";

createRoot(document.getElementById("game")!).render(
  <QueryClientProvider client={queryClient}>
    <WebsocketContextProvider />
    <StrictMode>
      <ThemeProvider>
        <Game />
      </ThemeProvider>
    </StrictMode>
  </QueryClientProvider>,
);
