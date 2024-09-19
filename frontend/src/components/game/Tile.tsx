import { useContext } from "react";
import { BoardContext } from "./Board";
import { TileType, Tile } from "@/types/api";
import { Goal } from "lucide-react";
import Property from "./Property";

interface TileProps {
  tile: Tile;
}

function BoardTile({ tile }: TileProps) {
  const { position, type } = tile;
  const { gridCellWidth, gridCellHeight, cornerSizeInPercent } =
    useContext(BoardContext);

  let left: string | number = -1;
  let right: string | number = -1;
  let top: string | number = -1;
  let bottom: string | number = -1;
  let gap = 1;

  let width: string | number = gridCellWidth - gap * 2;
  let height: string | number = gridCellHeight - gap * 2;

  if (position < 0 || position > 40) {
    console.error("Invalid tile id");
    return null;
  }

  if (position > 0 && position < 11) {
    left =
      `calc(${cornerSizeInPercent}% + ` +
      gridCellWidth * (position - 1) +
      `px + ${gap}px)`;
    height = `calc(${cornerSizeInPercent}% - ${gap}px)`;
  } else if (position > 10 && position < 21) {
    left = -1;
    right = 0;
    top =
      `calc(${cornerSizeInPercent}% + ` +
      gridCellHeight * (position - 11) +
      `px + ${gap}px)`;
    width = `calc(${cornerSizeInPercent}% - ${gap}px)`;
  } else if (position > 20 && position < 31) {
    left = -1;
    right =
      `calc(${cornerSizeInPercent}% + ` +
      gridCellWidth * (position - 21) +
      `px + ${gap}px)`;
    top = -1;
    bottom = 0;
    height = `calc(${cornerSizeInPercent}% - ${gap}px)`;
  } else if (position > 30 && position < 40) {
    left = 0;
    right = "unset";
    top = -1;
    bottom =
      `calc(${cornerSizeInPercent}% + ` +
      gridCellHeight * (position - 31) +
      `px + ${gap}px)`;
    width = `calc(${cornerSizeInPercent}% - ${gap}px)`;
  }

  if (position == 0 || position == 10 || position == 20 || position == 30) {
    width = `calc(${cornerSizeInPercent}% - ${gap}px)`;
    height = `calc(${cornerSizeInPercent}% - ${gap}px)`;
  }

  return (
    <div
      className="absolute z-10 flex items-center justify-center bg-yellow-300"
      style={{
        width: width,
        height: height,
        left: left !== -1 ? left : "unset",
        right: right !== -1 ? right : "unset",
        bottom: bottom !== -1 ? bottom : "unset",
        top: top !== -1 ? top : "unset",
        // boxShadow: "inset 0px 0px 8px -4px rgba(0,0,0,0.75)",
      }}
    >
      {type === TileType.START && (
        <div>
          <Goal />
        </div>
      )}
      {type === TileType.PROPERTY && <Property tile={tile} />}
      {(type === TileType.CHANCE || type === TileType.TAX) && (
        <div>
          <div className="text-center">{tile.position}</div>
        </div>
      )}
    </div>
  );
}

export default BoardTile;
