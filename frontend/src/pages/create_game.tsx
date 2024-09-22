import "vite/modulepreload-polyfill";

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "../index.css";

import CreateGame from "../components/create_game/CreateGame";
import { QueryClient, QueryClientProvider } from "react-query";

createRoot(document.getElementById("create-game")!).render(
  <StrictMode>
    <QueryClientProvider client={new QueryClient()}>
      <CreateGame />
    </QueryClientProvider>
  </StrictMode>,
);
