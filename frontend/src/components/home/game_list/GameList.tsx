import { useGames } from "@/hooks";
import GameRow from "./GameRow";
import { useTheme } from "@/stores/ThemeContext";
import { Button } from "@/components/ui/button";

function GameList() {
  const { data: games, isLoading: isGamesLoading } = useGames(true, true);
  const { bgColor } = useTheme();

  return (
    <div className="flex h-full w-full flex-1 flex-col gap-4">
      <div className="flex w-full">
        <h1 className="text-2xl">Active games</h1>
        <Button
          variant={"default"}
          className="ml-auto"
          onClick={() => (window.location.href = "/create_game")}
        >
          Create game
        </Button>
      </div>
      <div
        className="flex h-full flex-1 flex-col gap-2 rounded-xl py-4"
        style={{ backgroundColor: bgColor }}
      >
        {isGamesLoading ? (
          <h1>Loading...</h1>
        ) : (
          <>
            {games ? (
              games.games.map((game) => <GameRow key={game.uuid} game={game} />)
            ) : (
              <div>No games found</div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default GameList;
