import { useGameStore } from "@/entities/gameStore";
import { GameStatus } from "@/entities/types";
import { Lobby } from "./lobby/Lobby";
import { Game } from "./game/Game";
import { useTelegramColorScheme } from "@/shared/hooks/useTelegramTheme";
import { useAuthContext } from "@/entities/AuthProvider";
import { WebSocketContextProvider } from "@/app/providers/WebSocketProvider";

export const Main = () => {
  useTelegramColorScheme();
  const { me } = useAuthContext();
  const { game, processGameFrame } = useGameStore();

  const handleMessage = (message: any) => {
    let data = JSON.parse(message);
    processGameFrame(data);
  };

  return (
    // me.current_game is 100% present because there is a check in AuthProvider, maybe I should refactor this
    <WebSocketContextProvider gameUUID={me.current_game!.uuid} onMessage={handleMessage}>
      {!game ? <h1>Loading game</h1> : <>{game.status === GameStatus.WAITING ? <Lobby /> : <Game />}</>}
    </WebSocketContextProvider>
  );
};
