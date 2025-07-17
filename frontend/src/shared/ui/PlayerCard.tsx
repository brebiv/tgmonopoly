import type { Player } from "@/entities/types";
import type React from "react";
import { Avatar } from "./Avatar";
import { Card } from "./Card";
import { DicesIcon } from "lucide-react";
import { useGameStore } from "@/entities/gameStore";

interface PlayerCardProps {
  player?: Player;
}

export const PlayerCard: React.FC<PlayerCardProps> = ({ player }) => {
  const empty = player == null;
  const { game } = useGameStore();

  if (!game) {
    throw new Error("Game should be initialized");
  }

  return (
    <Card className="bg-background border-none px-2">
      {!empty && game.current_player === player.id && (
        <div className="absolute top-0 right-0">
          <DicesIcon className="text-primary" />
        </div>
      )}
      <div className="flex h-14 w-full gap-2">
        <div className="aspect-square h-full">
          <Avatar player={player} />
        </div>
        <div className="flex flex-col justify-center">
          <p>{empty ? "" : player.name}</p>
          {!empty && <p className="text-hint flex gap-1">$ {player.cash}</p>}
        </div>
      </div>
    </Card>
  );
};
