import type React from "react";
import type { Tile } from "@/entities/types";

interface TileProps {
  tile: Tile;
}

export const BoardTile: React.FC<TileProps> = ({ tile }) => {
  return <div className="bg-background">{tile.position}</div>;
};
