import { useGames } from "@/hooks";
import GameRow from "./GameRow";
import { useTheme } from "@/stores/ThemeContext";

function GameList() {
  const { data: games, isLoading: isGamesLoading } = useGames(true, true);
  const { bgColor } = useTheme();

  return (
    <div className="flex h-full w-full flex-1 flex-col gap-4">
      <h1 className="text-2xl">Games</h1>
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
