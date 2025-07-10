import { useGameStore } from "@/entities/gameStore";
import { GameStatus } from "@/entities/types";
import { useReactQuerySubscription } from "@/shared/hooks/useReactQuerySubscription";
import { Lobby } from "./lobby/Lobby";
import { Game } from "./game/Game";
import { useTelegramColorScheme } from "@/shared/hooks/useTelegramTheme";
import { useAuthContext } from "@/entities/AuthProvider";

export const Main = () => {
  useTelegramColorScheme();

  const { me } = useAuthContext();

  // current game is 100% present because there is a check in AuthProvider, maybe I should refactor this
  useReactQuerySubscription(me.current_game!.uuid);

  const { game } = useGameStore();
  if (!game) {
    return <h1>Loading game</h1>;
  }

  return <>{game.status === GameStatus.WAITING ? <Lobby /> : <Game />}</>;
};
