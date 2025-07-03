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
      className={cn(
        "rounded-full flex items-center justify-center w-full h-full border-2",
        {
          "border-hint border-dashed": empty,
        }
      )}
      style={{
        borderColor: player?.color,
      }}
    >
      {empty && <p className="text-hint">open</p>}
      {player && (
        <img
          className="rounded-full w-full h-full"
          src={player.avatar}
          alt={`Avatar for player ${player.name}`}
        />
      )}
    </div>
  );
};
