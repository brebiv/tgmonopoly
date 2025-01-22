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
import { WebsocketContextProvider } from "@/stores/WebsocketContext";
import { useWebsocketStore } from "@/stores/WebsocketStore";
import { WEBSOCKET_RECONNECT_DELAY } from "@/config";
import ConnectionError from "./ConnectionError";
import { Button } from "../ui/button";

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
  const [mountWebsocket, setMountWebsocket] = useState(true);

  const { secondaryBGColor } = useTheme();

  useEffect(() => {
    console.log("websocketConnected", websocketConnected);
    let interval: NodeJS.Timeout | undefined;
    if (!websocketConnected && websocketConnected !== undefined) {
      setMountWebsocket(false);

      interval = setInterval(() => {
        setMountWebsocket(true);
      }, WEBSOCKET_RECONNECT_DELAY);
    }

    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [websocketConnected]);

  const isLoading =
    auth == undefined || isMeLoading || game == undefined || players == undefined || !boardLoaded;

  if (isMeError) {
    return <Forbidden />;
  }

  // useReactQuerySubscription(gameUUID);

  if (game?.status === GameStatus.WAITING) {
    return <GameLobby />;
  }

  return (
    <>
      <div className="absolute z-50 mt-20 flex h-full w-full justify-center">
        <Button variant={"default"} onClick={() => setMountWebsocket(false)}>
          Trigger disconnect
        </Button>
      </div>
      {isLoading && <LoadingScreen />}
      {mountWebsocket && <WebsocketContextProvider />}
      {!isLoading && <ConnectionError show={!mountWebsocket || !websocketConnected} />}

      <div
        className="flex min-h-screen flex-col gap-4"
        style={{
          backgroundColor: secondaryBGColor,
        }}
      >
        {game?.status === GameStatus.FINISHED && <GameOverScreen />}
        <PlayersChipController players={players} boardLoaded={boardLoaded} />
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
