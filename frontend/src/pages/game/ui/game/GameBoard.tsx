import { TileRenderer } from "./TileRenderer";
import { PlayerChipController } from "./PlayerChipController";
import React from "react";
import { useGameStore } from "@/entities/gameStore";

interface GameBoardProps {
  children?: React.ReactNode;
}

export const GameBoard: React.FC<GameBoardProps> = ({ children }) => {
  const tilesLoaded = useGameStore((s) => s.tilesLoaded);

  return (
    <div className="relative aspect-square w-full">
      {tilesLoaded && <PlayerChipController />}
      <TileRenderer>{children}</TileRenderer>
    </div>
  );
};
