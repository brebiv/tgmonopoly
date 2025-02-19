import { useEffect, useState } from "react";
import Board from "./Board";

import { useAuth } from "@/hooks";
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
// import DebugPanel from "./DebugPanel";
import { useTheme } from "@/stores/ThemeContext";
import GameLog from "./GameLog/GameLog";
import TradeMenu from "./TradeMenu/TradeMenu";
import { useTradeStore } from "@/stores/TradeStore";
import { useWebsocketStore } from "@/stores/WebsocketStore";
import ConnectionError from "./ConnectionError";
// import TriggerDisconnectButton from "../debug/TriggerDisconnectButton";

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

  // const gameUUID = window.location.pathname.split("/")[2];
  const { data: auth, isLoading: isMeLoading, isError: isMeError } = useAuth(true);

  const [boardLoaded, setBoardLoaded] = useState(false);
  const { game, players } = useGameStore((state) => state);
  const { tradeMenuData } = useTradeStore();
  const { connected: websocketConnected } = useWebsocketStore();

  const { secondaryBGColor } = useTheme();

  const isLoading =
    auth == undefined || isMeLoading || game == undefined || players == undefined || !boardLoaded;

  if (isMeError) {
    return <Forbidden />;
  }

  if (game?.status === GameStatus.WAITING) {
    return (
      <GameLobby game={game!}>
        <GameLobby.Actions game={game!}></GameLobby.Actions>
      </GameLobby>
    );
  }

  return (
    <>
      {/* <div className="absolute z-50 mt-20 flex h-full w-full justify-center">
        <TriggerDisconnectButton />
      </div> */}
      {isLoading && <LoadingScreen />}

      {!isLoading && <ConnectionError show={!websocketConnected} />}

      <div
        className="relative flex min-h-screen flex-col gap-4"
        style={{
          backgroundColor: secondaryBGColor,
        }}
      >
        {game?.status === GameStatus.FINISHED && <GameOverScreen />}
        <PlayersChipController players={players} isGameLoading={isLoading} />
        {/* <BoardCenter>
        <DebugPanel />
        <TileInfo />
        </BoardCenter> */}
        <Board boardLoaded={boardLoaded} setBoardLoaded={setBoardLoaded}>
          {!tradeMenuData && <DiceController />}
          {!tradeMenuData && <TileInfo />}
          {tradeMenuData != null && <TradeMenu />}
          {!tradeMenuData && <GameLog />}
          {/* <DebugPanel /> */}
        </Board>
        <PlayersSection />
        <TurnMenu />
      </div>
    </>
  );
}

export default Game;
