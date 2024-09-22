import "vite/modulepreload-polyfill";

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { QueryClient, QueryClientProvider } from "react-query";
import "../index.css";

import Game from "../components/game/Game";

createRoot(document.getElementById("game")!).render(
  <StrictMode>
    <QueryClientProvider client={new QueryClient()}>
      <Game />
    </QueryClientProvider>
  </StrictMode>,
);
