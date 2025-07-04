import { useGameListStore } from "@/entities/gameListStore";
import { GameCard } from "./GameCard";
import { useWebsocketSubscription } from "@/shared/hooks/useWebsocketSubscription";

export const GameList = () => {
  const { games, setGames } = useGameListStore();
  const handleGamesStreamEvent = (data: any) => {
    console.log("Received event:", data);
    setGames(data.games);
  };

  useWebsocketSubscription("/ws/games/", handleGamesStreamEvent);

  return (
    <div className="flex flex-col w-full gap-3">
      {games && games?.map((game, i) => <GameCard key={i} game={game} />)}
    </div>
  );
};
