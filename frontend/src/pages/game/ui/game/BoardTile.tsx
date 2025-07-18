import type React from "react";
import type { Ownership, Tile } from "@/entities/types";
import { cn } from "@/shared/utils";
import { CloverIcon, CoinsIcon, Columns4Icon, GoalIcon, PiggyBankIcon, SirenIcon } from "lucide-react";
import { useGameBoardContext } from "@/entities/GameBoardContext";
import { useGameStore } from "@/entities/gameStore";

interface TileProps {
  tile: Tile;
  side: "top" | "right" | "bottom" | "left";
  ownership?: Ownership;
}

const PurchasableTile: React.FC<TileProps> = ({ tile, side, ownership }) => {
  const { boardConfig } = useGameBoardContext();
  const { getPlayerById } = useGameStore();
  const propertyGroup = boardConfig?.property_groups.find(
    (property_group) => property_group.id == tile.group,
  );

  if (!propertyGroup) {
    console.warn(`Could not find property group ${tile.group}`);
    return <h1>Could not find property group {tile.group}</h1>;
  }

  let price = ownership ? ownership.rent : tile.price;
  let owner = ownership && getPlayerById(ownership.player);

  return (
    <>
      {/* Group marker */}
      <div
        data-component="group-marker"
        className={cn("absolute items-center justify-center", {
          "-top-3 flex h-3 w-full": side == "top",
          "-right-3 flex h-full w-3": side == "right",
          "-bottom-3 flex h-3 w-full": side == "bottom",
          "-left-3 flex h-full w-3": side == "left",
        })}
        style={{ backgroundColor: propertyGroup.color }}
      >
        <p
          className={cn("text-xs text-white", {
            "rotate-90": side == "right",
            "-rotate-90": side == "left",
          })}
        >
          {price}
        </p>
      </div>
      {/* Image */}
      <div data-component="tile-image" className="z-10 flex h-full w-full items-center justify-center p-1">
        <img
          src={tile.icon}
          className={cn({
            "w-full": side == "top" || side == "bottom",
            "-rotate-90": tile.tile_type == "property" && (side == "top" || side == "bottom"),
            "h-full": side == "right" || side == "left",
          })}
        />
      </div>
      {/* Ownership marker */}
      {owner && (
        <div
          data-component="ownership-marker"
          className="absolute h-full w-full opacity-50"
          style={{ backgroundColor: owner.color }}
        ></div>
      )}
    </>
  );
};

export const BoardTile: React.FC<TileProps> = ({ tile, side, ownership }) => {
  const { tile_type } = tile;

  return (
    <div
      data-position={tile.position}
      data-iscorner={["start", "jail", "casino", "police"].includes(tile_type)}
      date-side={side}
      className="bg-background tile relative h-full w-full dark:bg-white"
    >
      {/* Inner content wrapper */}
      <div className="absolute flex h-full w-full items-center justify-center">
        {/* Tiles */}
        {tile_type == "property" && <PurchasableTile tile={tile} side={side} ownership={ownership} />}
        {tile_type == "utility" && <PurchasableTile tile={tile} side={side} ownership={ownership} />}
        {tile_type == "chance" && <CloverIcon color="black" />}
        {tile_type == "tax" && <PiggyBankIcon color="black" />}
        {/* Corners */}
        {tile_type == "start" && <GoalIcon color="black" />}
        {tile_type == "jail" && <Columns4Icon color="black" />}
        {tile_type == "casino" && <CoinsIcon color="black" />}
        {tile_type == "police" && <SirenIcon color="black" />}
      </div>
    </div>
  );
};
