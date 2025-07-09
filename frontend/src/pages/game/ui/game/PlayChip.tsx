import type { Player } from "@/entities/types";
import { PLAYER_CHIP_COLORS } from "@/shared/config";
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
      className="absolute z-10 rounded-full outline-2 transition-all duration-[var(--player-chip-move-duration)] ease-in-out"
      style={{
        backgroundColor: primaryColor,
        outlineColor: borderColor,
        left: x,
        top: y,
        width: size,
        height: size,
      }}
    ></div>
  );
};
