import type { Player } from "@/entities/types";
import type React from "react";

import cn from "classnames";

interface AvatarProps {
  player?: Player;
}

export const Avatar: React.FC<AvatarProps> = ({ player }) => {
  const empty = player == null;

  return (
    <div
      className={cn("flex h-full w-full items-center justify-center rounded-full border-2", {
        "border-hint border-dashed": empty,
      })}
      style={{
        borderColor: player?.color,
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
