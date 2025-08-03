import { useGameListStore } from "@/entities/gameListStore";
import { GameCard } from "./GameCard";
import { useWebsocketSubscription } from "@/shared/hooks/useWebsocketSubscription";

interface GameListProps {
  disabled?: boolean;
}

export const GameList = ({}: GameListProps) => {
  const { games, setGames } = useGameListStore();
  const handleGamesStreamEvent = (data: any) => {
    setGames(data.games);
  };

  useWebsocketSubscription("/ws/games/", handleGamesStreamEvent);

  return (
    <div className="flex w-full flex-col gap-3">
      {games.length > 0 ? (
        games?.map((game, i) => (
          <>
            <GameCard key={i} game={game} />
            <GameCard key={i + 1} game={game} />
            <GameCard key={i + 2} game={game} />
            <GameCard key={i + 3} game={game} />
            <GameCard key={i + 4} game={game} />
          </>
        ))
      ) : (
        <h2 className="text-center">There are no games. Create a new one!</h2>
      )}
    </div>
  );
};
