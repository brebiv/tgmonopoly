// @ts-ignore
import "vite/modulepreload-polyfill";

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import "@shared/styles/tailwind.css";

import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "../../shared/queryClient";
import { Lobby } from "./ui/Lobby";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <Lobby />
    </QueryClientProvider>
  </StrictMode>
);
