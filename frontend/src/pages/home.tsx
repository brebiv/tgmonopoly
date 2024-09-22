import "vite/modulepreload-polyfill";

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { QueryClient, QueryClientProvider } from "react-query";
import Home from "../components/home/Home";
import "../index.css";

createRoot(document.getElementById("home")!).render(
  <StrictMode>
    <QueryClientProvider client={new QueryClient()}>
      <Home />
    </QueryClientProvider>
  </StrictMode>,
);
