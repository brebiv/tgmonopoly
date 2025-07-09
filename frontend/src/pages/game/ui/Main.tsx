import { useGameStore } from "@/entities/gameStore";
import { GameStatus } from "@/entities/types";
import { useReactQuerySubscription } from "@/shared/hooks/useReactQuerySubscription";
import { Lobby } from "./lobby/Lobby";
import { Game } from "./game/Game";
import { useTelegramColorScheme } from "@/shared/hooks/useTelegramTheme";

export const Main = () => {
  useTelegramColorScheme();
  const pathname = URL.parse(location.href)?.pathname;
  const gameUUID = pathname?.split("/").pop();

  if (!gameUUID) {
    console.error("Could not get UUID from url");
    return;
  }

  useReactQuerySubscription(gameUUID);

  const { game } = useGameStore();
  if (!game) {
    return <h1>Loading game</h1>;
  }

  return <>{game.status === GameStatus.WAITING ? <Lobby /> : <Game />}</>;
};
