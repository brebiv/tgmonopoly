import { useGameStore } from "@/entities/gameStore";
import { PlayerCard } from "@/shared/ui/PlayerCard";
import type React from "react";

interface PlayersSectionProps {}

export const PlayersSection: React.FC<PlayersSectionProps> = () => {
  const players = useGameStore((s) => s.players);

  return (
    <div className="grid grid-cols-2 gap-2 px-3">
      {players.map((p, i) => (
        <PlayerCard key={i} player={p} />
      ))}
    </div>
  );
};
