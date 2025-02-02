import "vite/modulepreload-polyfill";

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { QueryClient, QueryClientProvider } from "react-query";
import Home from "../components/home/Home";
import "../index.css";
import { ThemeProvider } from "@/stores/ThemeContext";
import BrowseGames from "@/components/home/BrowseGames";

import { RouterProvider, createRouter, createRoute, createRootRoute } from "@tanstack/react-router";

const rootRoute = createRootRoute();

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/",
  component: () => {
    return <Home />;
  },
});

const gamesRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/games",
  component: () => {
    return <BrowseGames />;
  },
});

const routeTree = rootRoute.addChildren([indexRoute, gamesRoute]);

const router = createRouter({ routeTree });

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}

createRoot(document.getElementById("home")!).render(
  <StrictMode>
    <QueryClientProvider client={new QueryClient()}>
      <ThemeProvider>
        <RouterProvider router={router} />
        {/* <Home /> */}
      </ThemeProvider>
    </QueryClientProvider>
  </StrictMode>,
);
