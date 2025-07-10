import type { Player } from "@/entities/types";
import type React from "react";

interface PlayersSectionProps {
  players: Player[];
}

export const PlayersSection: React.FC<PlayersSectionProps> = ({ players }) => {
  return (
    <div className="grid grid-cols-2 gap-2 p-2">
      {players.map((_, i) => (
        <div key={i} className="bg-background flex items-center justify-center px-4 py-2">
          Player: {i}
        </div>
      ))}
    </div>
  );
};
