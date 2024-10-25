import { PLAYER_CHIP_COLORS } from "@/config";
import { useGame } from "@/hooks";
import { cn, getPlayerById, hexToRGBA } from "@/lib/utils";
import { useGameStore } from "@/stores/GameStore";
import { Ownership, Tile } from "@/types/api";
import clsx from "clsx";
import { Lock } from "lucide-react";
import { useEffect, useState } from "react";
import HouseIcon from "../ui/icons/HouseIcon";
import ApartmentIcon from "../ui/icons/ApartmentIcon";
import { useTheme } from "@/stores/ThemeContext";

interface PropertyProps {
  tile: Tile;
  imSelected: boolean;
  tileInfo: Tile | null;
}

function Property({ tile, imSelected, tileInfo }: PropertyProps) {
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
  const { data: game } = useGame();

  const [color, setColor] = useState<string>("");
  const [price, setPrice] = useState<number>(0);
  const [mortgaged, setMortgaged] = useState<boolean>(false);
  const [mortageTurnsLeft, setMortageTurnsLeft] = useState<number | undefined>(15);
  const [ownership, setOwnership] = useState<Ownership | null>(null);

  const { textColor, destructiveColor } = useTheme();

  useEffect(() => {
    let ownership = ownerships?.find((ownership) => ownership.property === tile.propertyData?.id);
    if (ownership) {
      if (players) {
        let player = getPlayerById(players, ownership.player);
        if (player) {
          let color = PLAYER_CHIP_COLORS[player.color as keyof typeof PLAYER_CHIP_COLORS][0];
          let opacity = 0.6;
          setColor(hexToRGBA(color, opacity));
          setPrice(tile.propertyData?.rent || 0);
          setMortgaged(ownership.mortgaged);
          setOwnership(ownership);
          if (ownership.mortage_last_turn) {
            setMortageTurnsLeft(ownership.mortage_last_turn - game!.turn);
          }
        }
      }
    } else {
      setColor("");
      setPrice(tile.propertyData?.price || 0);
      setMortgaged(false);
      setMortageTurnsLeft(undefined);
      setOwnership(null);
    }
  }, [ownerships, players, tile]);

  const rotationClass = clsx({
    "": side === "top" || side === "bottom",
    "rotate-90": side === "right",
    "-rotate-90": side === "left",
  });

  const rotationFlexClass = clsx({
    "flex-col": side === "right",
    "flex-col-reverse": side === "left",
  });

  return (
    <div
      className="relative flex h-full w-full flex-col items-center justify-center p-1"
      style={{
        backgroundColor: color || "",
        boxShadow: color ? `inset 0px 0px 4px 1px rgb(0, 0, 0, 0.5)` : "",
      }}
    >
      {mortgaged && (
        <div className="absolute z-10 flex h-full w-full items-center justify-center">
          <div className="absolute h-full w-full bg-black opacity-50"></div>
        </div>
      )}

      {/* Houses */}
      {ownership && ownership.houses > 0 && (
        <div
          className={
            side === "top"
              ? "absolute -bottom-0 z-20 h-2/4 w-full rounded-b-lg"
              : side === "right"
                ? "absolute -left-0 z-20 h-full w-2/4 rounded-l-lg"
                : side === "bottom"
                  ? "absolute -top-0 z-20 h-2/4 w-full rounded-t-lg"
                  : side === "left"
                    ? "absolute right-0 z-20 h-full w-2/4 rounded-r-lg"
                    : ""
          }
        >
          <div
            className={cn(
              "flex h-full w-full flex-wrap justify-center",
              `${side === "right" || side === "bottom" ? "items-start" : "items-end"}`,
              rotationFlexClass,
            )}
            style={{
              color: textColor,
            }}
          >
            {ownership.houses == 5 ? (
              <ApartmentIcon
                className={cn("h-full w-full", rotationClass)}
                outline="#FFD700"
                fill="#403703"
              />
            ) : (
              <>
                {Array.from({ length: ownership.houses }, (_, i) => (
                  <HouseIcon key={`${tile.id}-${i}`} className={cn("h-3 w-3", rotationClass)} />
                ))}
              </>
            )}
          </div>
        </div>
      )}

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
        {tileInfo && !imSelected && (
          <div className="absolute z-10 h-full w-full bg-black opacity-50"></div>
        )}
        <div
          className="flex h-full w-full items-center justify-center"
          style={{
            color: textColor,
          }}
        >
          {mortgaged ? (
            <Lock
              className={cn(
                `z-10 h-3 w-3 ${side === "right" ? "rotate-90" : ""} ${side === "left" ? "-rotate-90" : ""} ${side === "left" ? "-rotate-90" : ""}`,
              )}
              style={{
                color: textColor,
              }}
            />
          ) : (
            <>
              {(side == "top" || side == "bottom") && <p className="text-xs">{price}</p>}
              {side == "right" && <p className="rotate-90 text-xs">{price}</p>}
              {side == "left" && <p className="-rotate-90 text-xs">{price}</p>}
            </>
          )}
        </div>
      </div>

      {/* Mortage marker */}
      {mortgaged && (
        <div
          className={
            side === "top"
              ? "absolute -bottom-4 z-20 h-5 w-full rounded-b-lg"
              : side === "right"
                ? "absolute -left-4 z-20 h-full w-4 rounded-l-lg"
                : side === "bottom"
                  ? "absolute -top-4 z-20 h-4 w-full rounded-t-lg"
                  : side === "left"
                    ? "absolute -right-4 z-20 h-full w-4 rounded-r-lg"
                    : ""
          }
          style={{
            backgroundColor: destructiveColor,
          }}
        >
          {tileInfo && !imSelected && (
            <div className="absolute z-10 h-full w-full rounded-b-lg bg-black opacity-50"></div>
          )}
          <div
            className={cn("flex h-full w-full items-center justify-center", rotationFlexClass)}
            style={{
              color: textColor,
            }}
          >
            <p className={cn("text-xs", rotationClass)}>{mortageTurnsLeft}</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default Property;
