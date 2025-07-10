// @ts-ignore
import "vite/modulepreload-polyfill";

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import "@shared/styles/tailwind.css";

import { HomePage } from "./ui/HomePage";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "../../shared/queryClient";
import { AuthContextProvider } from "@/entities/AuthProvider";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <AuthContextProvider>
        <HomePage />
      </AuthContextProvider>
    </QueryClientProvider>
  </StrictMode>,
);
