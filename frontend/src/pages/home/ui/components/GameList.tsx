import type { Game } from "@/entities/types";
import { GameCard } from "./GameCard";
import type React from "react";

interface GameListProps {
  games?: Game[];
}

export const GameList: React.FC<GameListProps> = ({ games }) => {
  console.log("gams", games);

  return (
    <div className="flex flex-col w-full gap-3">
      {games && games?.map((game, i) => <GameCard key={i} game={game} />)}
    </div>
  );
};
