import { useEffect } from "react";
import Board from "./Board";
import { QueryClient, QueryClientProvider } from "react-query";

function Game() {
  useEffect(() => {
    // @ts-ignore
    window.Telegram.WebApp.BackButton.hide();
  }, []);

  return (
    <QueryClientProvider client={new QueryClient()}>
      <div
        className="flex min-h-screen flex-col"
        style={{
          backgroundColor:
            // @ts-ignore
            window.Telegram.WebApp.themeParams.bg_color || "#334155",
        }}
      >
        <Board />
      </div>
    </QueryClientProvider>
  );
}

export default Game;
