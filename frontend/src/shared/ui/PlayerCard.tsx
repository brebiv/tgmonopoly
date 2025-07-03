import type { Player } from "@/entities/types";
import type React from "react";
import { Avatar } from "./Avatar";
import { Card } from "./Card";

interface PlayerCardProps {
  player?: Player;
}

export const PlayerCard: React.FC<PlayerCardProps> = ({ player }) => {
  const empty = player == null;
  return (
    <Card className="bg-background border-none !px-0">
      <div className="w-full h-14 flex gap-2">
        <div className="h-full aspect-square">
          <Avatar player={player} />
        </div>
        <div className="flex flex-col justify-center">
          <p>{empty ? "" : player.name}</p>
          {!empty && <p className="flex gap-1 text-hint">$ {player.cash}</p>}
        </div>
      </div>
    </Card>
  );
};
