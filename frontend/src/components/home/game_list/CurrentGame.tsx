import { Button } from "@/components/ui/button";
import { useAuth, useGame, usePlayers, useReactQuerySubscription } from "@/hooks";
import GameLobby from "@/components/game/GameLobby";
import axios from "axios";
import { GameStatus } from "@/types/api";

function CurrentGame() {
  const { data: me } = useAuth();
  useReactQuerySubscription(me?.current_game_info?.uuid!);

  const { data: game } = useGame();
  const { data: players } = usePlayers();

  if (!game) {
    return "Loading...";
  }

  return (
    <div className="flex h-full w-full flex-1 flex-col gap-4" id="current-game">
      <div className="flex w-full flex-1 flex-col gap-4">
        <h1 className="text-2xl">Your current game</h1>
        <GameLobby game={game} players={players} className="h-full p-0">
          <GameLobby.Actions game={game}>
            <Button
              variant={"default"}
              className="w-full font-semibold"
              onClick={() => {
                window.location.href = "/game/" + me?.current_game_info?.uuid;
              }}
            >
              Reconnect
            </Button>
            {game.status === GameStatus.WAITING && (
              <Button
                variant={"destructive"}
                className="w-full font-semibold"
                onClick={() => {
                  axios.get("/api/abandon_game/" + me?.current_game_info?.uuid).then(() => {
                    window.location.href = "/";
                  });
                }}
              >
                Abandon
              </Button>
            )}
          </GameLobby.Actions>
        </GameLobby>
      </div>
    </div>
  );
}

export default CurrentGame;
