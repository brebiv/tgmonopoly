import { useEffect } from "react";
import Board from "./Board";

import { useGame, usePlayers } from "@/hooks";

function Game() {
  useEffect(() => {
    // @ts-ignore
    // window.Telegram.WebApp.BackButton.hide();
    window.Telegram.WebApp.BackButton.show();
    // @ts-ignore
    window.Telegram.WebApp.BackButton.onClick(() => {
      window.location.href = "/";
      // @ts-ignore
      window.Telegram.WebApp.BackButton.hide();
      return true;
    });
  }, []);

  const { data: game, refetch: refetchGame } = useGame(
    window.location.pathname.split("/")[2],
  );

  const { data: players, refetch: refetchPlayers } = usePlayers(
    window.location.pathname.split("/")[2],
  );

  useEffect(() => {
    refetchGame();
    refetchPlayers();
  }, []);

  useEffect(() => {
    if (game) {
      console.log("Game", game);
    }
    if (players) {
      console.log("Players", players);
    }
  }, [game, players]);

  return (
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
  );
}

export default Game;
