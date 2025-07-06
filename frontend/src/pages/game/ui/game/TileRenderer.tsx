import type { Tile } from "@/entities/types";
import React from "react";
import { BoardTile } from "./BoardTile";

interface TileRendererProps {
  tiles: Tile[];
}

export const TileRenderer: React.FC<TileRendererProps> = ({ tiles }) => {
  if (!tiles) {
    return <h1>Loading</h1>;
  }

  return (
    <div
      id="tiles"
      className="bg-secondary-background relative top-0 left-0 grid h-full w-full gap-[2px] p-3"
      style={{
        gridTemplateColumns: "13% repeat(9, auto) 13%",
        gridTemplateRows: "13% repeat(9, auto) 13%",
      }}
    >
      {/* Top */}
      <div className="relative col-span-11 row-start-1 grid grid-cols-subgrid gap-[2px]">
        {tiles.slice(0, 11).map((tile) => (
          <BoardTile tile={tile} side="top" />
        ))}
      </div>
      {/* Right */}
      <div className="col-start-11 row-span-10 row-start-2 grid grid-cols-subgrid grid-rows-subgrid gap-[2px]">
        {tiles.slice(11, 21).map((tile) => (
          <BoardTile tile={tile} side="right" />
        ))}
      </div>
      {/* Bottom */}
      <div
        dir="rtl"
        className="col-span-11 col-start-11 col-end-1 row-start-11 grid grid-cols-subgrid grid-rows-subgrid gap-[2px]"
      >
        {tiles.slice(21, 31).map((tile) => (
          <BoardTile tile={tile} side="bottom" />
        ))}
      </div>
      {/* Left */}
      <div className="col-span-1 col-start-1 row-span-9 row-start-2 grid grid-cols-subgrid grid-rows-subgrid gap-[2px]">
        {tiles
          .slice(31, 40)
          .reverse()
          .map((tile) => (
            <BoardTile tile={tile} side="left" />
          ))}
      </div>
    </div>
  );
};
