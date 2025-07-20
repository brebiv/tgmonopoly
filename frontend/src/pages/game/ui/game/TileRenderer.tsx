import React, { useEffect } from "react";
import { BoardTile } from "./BoardTile";
import { useGameStore } from "@/entities/gameStore";

interface TileRendererProps {
  children?: React.ReactNode;
}

export const TileRenderer: React.FC<TileRendererProps> = ({ children }) => {
  const boardConfig = useGameStore((s) => s.boardConfig);
  const ownerships = useGameStore((s) => s.ownerships);
  const setTilesLoaded = useGameStore((s) => s.setTilesLoaded);

  if (!boardConfig) {
    return <h1>Loading tile renderer</h1>;
  }

  const { tiles } = boardConfig;

  useEffect(() => {
    setTilesLoaded(true);
  }, []);

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
        {tiles.slice(0, 11).map((tile, i) => {
          let ownership = ownerships.find((o) => o.tile_position === tile.position);
          return <BoardTile key={i} tile={tile} side="top" ownership={ownership} />;
        })}
      </div>
      {/* Right */}
      <div className="col-start-11 row-span-10 row-start-2 grid grid-cols-subgrid grid-rows-subgrid gap-[2px]">
        {tiles.slice(11, 21).map((tile, i) => {
          let ownership = ownerships.find((o) => o.tile_position === tile.position);
          return <BoardTile key={i} tile={tile} side="right" ownership={ownership} />;
        })}
      </div>
      {/* Bottom */}
      <div
        dir="rtl"
        className="col-span-11 col-start-11 col-end-1 row-start-11 grid grid-cols-subgrid grid-rows-subgrid gap-[2px]"
      >
        {tiles.slice(21, 31).map((tile, i) => {
          let ownership = ownerships.find((o) => o.tile_position === tile.position);
          return <BoardTile key={i} tile={tile} side="bottom" ownership={ownership} />;
        })}
      </div>
      {/* Left */}
      <div className="col-span-1 col-start-1 row-span-9 row-start-2 grid grid-cols-subgrid grid-rows-subgrid gap-[2px]">
        {tiles
          .slice(31, 40)
          .reverse()
          .map((tile, i) => {
            let ownership = ownerships.find((o) => o.tile_position === tile.position);
            return <BoardTile key={i} tile={tile} side="left" ownership={ownership} />;
          })}
      </div>
      {/* Center */}
      <div
        id="board-center"
        className="relative col-span-9 col-start-2 row-span-9 row-start-2 overflow-y-scroll"
      >
        {children}
      </div>
    </div>
  );
};
