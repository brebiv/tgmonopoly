import { useContext, useEffect, useRef, useState } from "react";
import { BoardContext } from "./Board";
import { TileType, Tile } from "@/types/api";
import { Clover, Coins, Columns4, Goal, PiggyBank, Siren } from "lucide-react";
import Property from "./Property";
import { useTileInfoStore } from "@/stores/TileInfoStore";

interface TileProps {
  tile: Tile;
}

function BoardTile({ tile }: TileProps) {
  const { position, type } = tile;
  const { gridCellWidth, gridCellHeight, cornerSizeInPercent } = useContext(BoardContext);
  const tileRef = useRef<HTMLDivElement>(null);

  const { setTileInfo, tile: tileInfo } = useTileInfoStore();
  const [imSelected, setImSelected] = useState(true);

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
    left = `calc(${cornerSizeInPercent}% + ` + gridCellWidth * (position - 1) + `px + ${gap}px)`;
    height = `calc(${cornerSizeInPercent}% - ${gap}px)`;
  } else if (position > 10 && position < 21) {
    left = -1;
    right = 0;
    top = `calc(${cornerSizeInPercent}% + ` + gridCellHeight * (position - 11) + `px + ${gap}px)`;
    width = `calc(${cornerSizeInPercent}% - ${gap}px)`;
  } else if (position > 20 && position < 31) {
    left = -1;
    right = `calc(${cornerSizeInPercent}% + ` + gridCellWidth * (position - 21) + `px + ${gap}px)`;
    top = -1;
    bottom = 0;
    height = `calc(${cornerSizeInPercent}% - ${gap}px)`;
  } else if (position > 30 && position < 40) {
    left = 0;
    right = "unset";
    top = -1;
    bottom =
      `calc(${cornerSizeInPercent}% + ` + gridCellHeight * (position - 31) + `px + ${gap}px)`;
    width = `calc(${cornerSizeInPercent}% - ${gap}px)`;
  }

  if (position == 0 || position == 10 || position == 20 || position == 30) {
    width = `calc(${cornerSizeInPercent}% - ${gap}px)`;
    height = `calc(${cornerSizeInPercent}% - ${gap}px)`;
  }

  useEffect(() => {
    if (tileInfo && tileInfo.position === position) {
      setImSelected(true);
    } else {
      setImSelected(false);
    }
  }, [tileInfo]);

  return (
    <div
      ref={tileRef}
      data-position={position}
      className="tile absolute z-10 flex items-center justify-center"
      style={{
        width: width,
        height: height,
        left: left !== -1 ? left : "unset",
        right: right !== -1 ? right : "unset",
        bottom: bottom !== -1 ? bottom : "unset",
        top: top !== -1 ? top : "unset",
        // boxShadow: "inset 0px 0px 8px -4px rgba(0,0,0,0.75)",
        backgroundColor:
          // @ts-ignore
          window.Telegram.WebApp.themeParams.text_color || "white",
      }}
      onClick={() => {
        setTileInfo(tile, tileRef);
      }}
    >
      {tileInfo && !imSelected && (
        <div className="absolute z-10 h-full w-full bg-black opacity-50"></div>
      )}
      {type === TileType.START && (
        <div>
          <Goal />
        </div>
      )}
      {type === TileType.JAIL && (
        <div>
          <Columns4 />
        </div>
      )}
      {type === TileType.CASINO && (
        <div>
          <Coins />
        </div>
      )}
      {type === TileType.POLICE && (
        <div>
          <Siren />
        </div>
      )}
      {(type === TileType.PROPERTY || type === TileType.UTILITY) && (
        <Property tile={tile} imSelected={imSelected} tileInfo={tileInfo} />
      )}
      {type === TileType.CHANCE && (
        <div>
          <Clover />
        </div>
      )}
      {type === TileType.TAX && (
        <div>
          <PiggyBank />
        </div>
      )}
    </div>
  );
}

export default BoardTile;
