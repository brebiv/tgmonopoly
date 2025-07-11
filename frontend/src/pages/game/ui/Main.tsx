import { useGameStore } from "@/entities/gameStore";
import { GameFrameTypes, GameStatus, type GameFrame } from "@/entities/types";
import { Lobby } from "./lobby/Lobby";
import { Game } from "./game/Game";
import { useTelegramColorScheme } from "@/shared/hooks/useTelegramTheme";
import { useAuthContext } from "@/entities/AuthProvider";
import { WebSocketContextProvider } from "@/app/providers/WebSocketProvider";

export const Main = () => {
  useTelegramColorScheme();
  const { me } = useAuthContext();
  const { game, processInitialGameFrame, processEventGameFrame } = useGameStore();

  const handleMessage = (message: any) => {
    let data: GameFrame = JSON.parse(message);
    if (data.type === GameFrameTypes.GAME_INITIAL) {
      processInitialGameFrame(data);
    } else if (data.type === GameFrameTypes.GAME_EVENT) {
      processEventGameFrame(data);
    }
  };

  return (
    // me.current_game is 100% present because there is a check in AuthProvider, maybe I should refactor this
    <WebSocketContextProvider gameUUID={me.current_game!.uuid} onMessage={handleMessage}>
      {!game ? <h1>Loading game</h1> : <>{game.status === GameStatus.WAITING ? <Lobby /> : <Game />}</>}
    </WebSocketContextProvider>
  );
};
