import { useGameStore } from "@/entities/gameStore";
import { GameBoard } from "./GameBoard";
import { PlayersSection } from "./PlayersSection";

export const Game = () => {
  const { players } = useGameStore();

  return (
    <div className="bg-secondary-background flex h-screen flex-col gap-2">
      <GameBoard />
      <PlayersSection players={players} />
    </div>
  );
};
