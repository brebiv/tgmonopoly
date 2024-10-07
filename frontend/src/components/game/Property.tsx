import { PLAYER_CHIP_COLORS } from "@/config";
import { getPlayerById, hexToRGBA } from "@/lib/utils";
import { useGameStore } from "@/stores/GameStore";
import { Tile } from "@/types/api";
import { useEffect, useState } from "react";

interface PropertyProps {
  tile: Tile;
}

function Property({ tile }: PropertyProps) {
  let side: "top" | "right" | "bottom" | "left" | undefined = undefined;

  if (tile.position >= 0 && tile.position < 10) {
    side = "top";
  } else if (tile.position >= 10 && tile.position < 20) {
    side = "right";
  } else if (tile.position >= 20 && tile.position < 30) {
    side = "bottom";
  } else if (tile.position >= 30 && tile.position < 40) {
    side = "left";
  }

  const { ownerships, players } = useGameStore((state) => state);
  const [color, setColor] = useState<string>("");
  const [price, setPrice] = useState<number>(0);

  useEffect(() => {
    let ownership = ownerships?.find((ownership) => ownership.property === tile.propertyData?.id);
    // setOwnership(ownership);
    if (ownership) {
      if (players) {
        // const player = useGameStore.getState().players?.find((player) => player.id === ownership.player);
        let player = getPlayerById(players, ownership.player);
        if (player) {
          // setPlayer(player);
          let color = PLAYER_CHIP_COLORS[player.color as keyof typeof PLAYER_CHIP_COLORS][0];
          let opacity = 0.6;
          setColor(hexToRGBA(color, opacity));
          setPrice(tile.propertyData?.rent || 0);
        }
      }
    } else {
      setColor("");
      setPrice(tile.propertyData?.price || 0);
    }
  }, [ownerships, players, tile]);

  return (
    <div
      className="relative flex h-full w-full flex-col items-center justify-center p-1"
      style={{
        backgroundColor: color || "unset",
        boxShadow: color ? `inset 0px 0px 4px 1px rgb(0, 0, 0, 0.5)` : "unset",
      }}
    >
      {/* Body */}
      {(side == "top" || side == "bottom") && (
        <img src={tile.propertyData?.icon} className="-rotate-90" />
      )}
      {(side == "right" || side == "left") && (
        <img src={tile.propertyData?.icon} className="h-full" />
      )}
      {/* Group color marker */}
      <div
        className={
          side === "top"
            ? "absolute -top-3 h-3 w-full"
            : side === "right"
              ? "absolute -right-3 h-full w-3"
              : side === "bottom"
                ? "absolute -bottom-3 h-3 w-full"
                : side === "left"
                  ? "absolute -left-3 h-full w-3"
                  : ""
        }
        style={{
          backgroundColor: `var(--group-color-${tile.propertyData?.group_id})`,
        }}
      >
        <div
          className="flex h-full w-full items-center justify-center"
          style={{
            color:
              // @ts-ignore
              window.Telegram.WebApp.themeParams.text_color || "white",
          }}
        >
          {(side == "top" || side == "bottom") && (
            <p className="text-xs">{price}</p>
          )}
          {side == "right" && <p className="rotate-90 text-xs">{price}</p>}
          {side == "left" && <p className="-rotate-90 text-xs">{price}</p>}
        </div>
      </div>
    </div>
  );
}

export default Property;
