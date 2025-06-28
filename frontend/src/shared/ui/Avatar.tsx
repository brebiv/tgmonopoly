import type { Player } from "@/entities/types";
import type React from "react";

import cn from "classnames";

interface AvatarProps {
  player?: Player;
  empty?: boolean;
}

export const Avatar: React.FC<AvatarProps> = ({ player, empty }) => {
  return (
    <div
      className={cn("rounded-full flex items-center justify-center", {
        "border-[1px] border-hint border-dashed": empty,
      })}
    >
      {empty && <p className="text-hint">waiting</p>}
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
