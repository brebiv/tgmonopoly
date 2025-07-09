import { TileRenderer } from "./TileRenderer";
import { PlayerChipController } from "./PlayerChipController";
import React, { useState } from "react";
import type { BoardConfig, Player } from "@/entities/types";
import { GameBoardContextProvider } from "@/entities/GameBoardContext";

interface GameBoardProps {
  players: Player[];
  boardConfig: BoardConfig;
  children?: React.ReactNode;
}

export const GameBoard: React.FC<GameBoardProps> = ({ players, boardConfig, children }) => {
  const [tilesLoaded, setTilesLoaded] = useState(false);

  const handleTileLoaded = () => {
    setTilesLoaded(true);
  };

  return (
    <GameBoardContextProvider boardConfig={boardConfig}>
      <div className="relative aspect-square w-full">
        {tilesLoaded && <PlayerChipController players={players} />}
        <TileRenderer tiles={boardConfig.tiles} onLoad={() => handleTileLoaded()}>
          {children}
        </TileRenderer>
      </div>
    </GameBoardContextProvider>
  );
};
