import { useGameStore } from "@/entities/gameStore";
import { GameBoard } from "./GameBoard";
import { PlayersSection } from "./PlayersSection";

export const Game = () => {
  const { players } = useGameStore();
  return (
    <div className="flex flex-col gap-2 h-screen">
      <GameBoard />
      <PlayersSection players={players} />
    </div>
  );
};
