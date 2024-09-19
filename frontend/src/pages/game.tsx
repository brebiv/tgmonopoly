import "vite/modulepreload-polyfill";

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "../index.css";

import Game from "../components/game/Game";

createRoot(document.getElementById("game")!).render(
  <StrictMode>
    <Game />
  </StrictMode>
);
