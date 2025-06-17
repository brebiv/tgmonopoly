// @ts-ignore
import "vite/modulepreload-polyfill";

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

// import "../../shared/styles/tailwind.css";
import "@shared/styles/tailwind.css";

import { HomePage } from "./HomePage";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <HomePage />
  </StrictMode>
);
