import { useAuth, useGames } from "@/hooks";
import GameListRow from "./GameListRow";
import { useTheme } from "@/stores/ThemeContext";
import { Button } from "@/components/ui/button";

function GameList() {
  const { data: games, isLoading: isGamesLoading } = useGames(true, true);
  const { bgColor, hintColor } = useTheme();
  const { data: authMe } = useAuth();

  return (
    <div className="flex h-full w-full flex-1 flex-col gap-4">
      <div className="flex w-full">
        <h1 className="text-2xl">Active games</h1>
        {authMe?.current_game_link ? (
          <Button
            variant={"default"}
            className="ml-auto"
            onClick={() => (window.location.href = authMe?.current_game_link!)}
            // disabled={authMe?.permissions.create_game == false}
          >
            Reconnect
          </Button>
        ) : (
          <Button
            variant={"default"}
            className="ml-auto"
            onClick={() => (window.location.href = "/create_game")}
            // disabled={authMe?.permissions.create_game == false}
          >
            Create game
          </Button>
        )}
      </div>
      <div
        className="flex h-full flex-1 flex-col gap-2 rounded-xl py-2"
        style={{ backgroundColor: bgColor }}
      >
        {isGamesLoading ? (
          <h1>Loading...</h1>
        ) : (
          <>
            {games && games.games.length > 0 ? (
              games.games.map((game) => <GameListRow key={game.uuid} game={game} />)
            ) : (
              <div
                className="flex w-full items-center justify-center pt-2"
                style={{
                  color: hintColor,
                }}
              >
                No active games
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default GameList;
