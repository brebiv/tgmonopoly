import type { Player } from "@/entities/types";
import { PLAYER_CHIP_COLORS, PLAYER_CHIP_MOVE_DURATION_MS } from "@/shared/config";
import type React from "react";

interface PlayerChipProps {
  player: Player;
  size: number;
  x: number;
  y: number;
}

export const PlayerChip: React.FC<PlayerChipProps> = ({ player, size, x, y }) => {
  const [primaryColor, borderColor] = Object(PLAYER_CHIP_COLORS)[player.color];

  return (
    <div
      className="absolute z-20 rounded-full outline-2 transition-all ease-in-out"
      style={{
        backgroundColor: primaryColor,
        outlineColor: borderColor,
        transitionDuration: `${PLAYER_CHIP_MOVE_DURATION_MS}ms`,
        left: x,
        top: y,
        width: size,
        height: size,
      }}
    ></div>
  );
};
