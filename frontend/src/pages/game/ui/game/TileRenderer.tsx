import type { Tile } from "@/entities/types";
import React from "react";
import { BoardTile } from "./BoardTile";

interface TileRendererProps {
  tiles: Tile[];
}

export const TileRenderer: React.FC<TileRendererProps> = ({ tiles }) => {
  return (
    <div
      id="tiles"
      className="bg-secondary-background relative top-0 left-0 grid h-full w-full [grid-template-columns:14%_repeat(9,_auto)_14%] [grid-template-rows:14%_repeat(9,_auto)_14%] gap-[1px] p-3"
    >
      <div className="col-span-11 row-start-1 grid grid-cols-subgrid gap-[1px]">
        {tiles.slice(0, 11).map((tile) => (
          <BoardTile tile={tile} />
        ))}
      </div>
      <div className="col-start-11 row-span-11 row-start-2 grid grid-cols-subgrid grid-rows-subgrid gap-[1px]">
        {tiles.slice(11, 21).map((tile) => (
          <BoardTile tile={tile} />
        ))}
      </div>
      <div
        dir="rtl"
        className="col-span-11 col-start-11 col-end-1 row-start-11 grid grid-cols-subgrid grid-rows-subgrid gap-[1px]"
      >
        {tiles.slice(21, 31).map((tile) => (
          <BoardTile tile={tile} />
        ))}
      </div>
      <div className="col-span-1 col-start-1 row-span-9 row-start-2 grid grid-cols-subgrid grid-rows-subgrid gap-[1px]">
        {tiles
          .slice(31, 40)
          .reverse()
          .map((tile) => (
            <BoardTile tile={tile} />
          ))}
      </div>
    </div>
  );
};
