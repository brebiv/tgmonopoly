import { useEffect, useState } from "react";
import Board from "./Board";

import { useAuth, useReactQuerySubscription } from "@/hooks";
import PlayersChipController from "./PlayersChipController";
import Forbidden from "../Forbidden";
import LoadingScreen from "../LoadingScreen";
import DiceController from "./DiceController";
import { GameStatus } from "@/types/api";
import { useGameStore } from "@/stores/GameStore";
import PlayersSection from "./PlayersSection";
import TurnMenu from "./TurnMenu/TurnMenu";
import GameLobby from "./GameLobby";
import GameOverScreen from "./GameOverScreen";
import TileInfo from "./TileInfo";
import BoardCenter from "./BoardCenter";
import DebugPanel from "./DebugPanel";

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

  const gameUUID = window.location.pathname.split("/")[2];
  const { data: auth, isLoading: isMeLoading, isError: isMeError } = useAuth(true);

  const [boardLoaded, setBoardLoaded] = useState(false);
  const { game, players } = useGameStore((state) => state);

  if (isMeError) {
    return <Forbidden />;
  }

  useReactQuerySubscription(gameUUID);

  if (game?.status === GameStatus.WAITING) {
    return <GameLobby />;
  }

  return (
    <div
      className="flex min-h-screen flex-col gap-4"
      style={{
        backgroundColor:
          // @ts-ignore
          window.Telegram.WebApp.themeParams.secondary_bg_color || "#334155",
      }}
    >
      {(auth == undefined ||
        isMeLoading ||
        game == undefined ||
        players == undefined ||
        !boardLoaded) && <LoadingScreen />}
      {game?.status === GameStatus.FINISHED && <GameOverScreen />}
      <PlayersChipController players={players} boardLoaded={boardLoaded} />
      <DiceController />
      <BoardCenter>
        <DebugPanel />
        <TileInfo />
      </BoardCenter>
      <Board boardLoaded={boardLoaded} setBoardLoaded={setBoardLoaded} />
      <PlayersSection />
      <TurnMenu />
    </div>
  );
}

export default Game;
