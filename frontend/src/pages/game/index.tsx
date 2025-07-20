// @ts-ignore
import "vite/modulepreload-polyfill";

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
// import { ReactQueryDevtools } from "@tanstack/react-query-devtools";

import "@shared/styles/tailwind.css";
import "@shared/styles/animation.css";

import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "../../shared/queryClient";
import { Main } from "./ui/Main";
import { AuthContextProvider } from "@/entities/AuthProvider";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <AuthContextProvider currentGameUUIDMustMatchWithURL>
        {/* <ReactQueryDevtools initialIsOpen={false} /> */}
        <Main />
      </AuthContextProvider>
    </QueryClientProvider>
  </StrictMode>,
);
