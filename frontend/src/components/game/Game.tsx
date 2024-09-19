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
      <div className="flex min-h-screen flex-col bg-green-100">
        <Board />
      </div>
    </QueryClientProvider>
  );
}

export default Game;
