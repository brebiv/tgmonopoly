import type { Player } from "@/entities/types";
import { PlayerCard } from "@/shared/ui/PlayerCard";
import type React from "react";

interface PlayersSectionProps {
  players: Player[];
}

export const PlayersSection: React.FC<PlayersSectionProps> = ({ players }) => {
  return (
    <div className="grid grid-cols-2 gap-2 px-3">
      {players.map((p, i) => (
        <PlayerCard key={i} player={p} />
      ))}
    </div>
  );
};
