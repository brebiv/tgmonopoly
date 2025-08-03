import type { Game } from "@/entities/types";
import { JoinGameButton } from "@/features/join-game/JoinGameButton";
import { Avatar } from "@/shared/ui/Avatar";
import { Card } from "@/shared/ui/Card";
import { UsersIcon } from "lucide-react";

interface GameCardProps {
  game: Game;
}

export const GameCard: React.FC<GameCardProps> = ({ game }) => {
  return (
    <Card className="">
      <div className="flex items-center justify-between gap-4">
        <h2>Default game</h2>
        <p className="text-primary flex gap-2 font-mono">
          <UsersIcon />
          {game.players.length}/{game.max_players}
        </p>
      </div>
      <div className="flex justify-between gap-4">
        <div
          className="grid h-full gap-2"
          style={{
            gridTemplateColumns: `repeat(${game.max_players}, minmax(0, 1fr))`,
          }}
        >
          {Array.from({ length: game.max_players }).map((_, i) => {
            return game.players[i] ? (
              <div key={i} className="h-16">
                <Avatar player={game.players[i]} />
              </div>
            ) : (
              <div className="h-16">
                <Avatar key={i} />
              </div>
            );
          })}
        </div>
        <div className="flex items-center gap-2">
          <JoinGameButton gameUUID={game.uuid} />
        </div>
      </div>
    </Card>
  );
};
