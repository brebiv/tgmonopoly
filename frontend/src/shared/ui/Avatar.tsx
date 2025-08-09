import type { Player } from "@/entities/types";
import type React from "react";

import cn from "classnames";
import { PLAYER_CHIP_COLORS } from "../config";

interface AvatarProps {
  player?: Player;
}

export const Avatar: React.FC<AvatarProps> = ({ player }) => {
  const empty = player == null;

  return (
    <div
      className={cn("flex h-full w-full items-center justify-center rounded-full border-3", {
        "border-hint border-dashed": empty,
      })}
      style={{
        // @ts-ignore
        borderColor: player ? `${PLAYER_CHIP_COLORS[player.color][0]}` : undefined,
      }}
    >
      {empty && <p className="text-hint">open</p>}
      {player && (
        <img
          className="h-full w-full rounded-full"
          src={player.avatar}
          alt={`Avatar for player ${player.name}`}
        />
      )}
    </div>
  );
};
