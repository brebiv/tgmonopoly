import type { Game } from "@/entities/types";
import { JoinGameButton } from "@/features/join-game/JoinGameButton";
import { Avatar } from "@/shared/ui/Avatar";
import { UsersIcon } from "lucide-react";

interface GameCardProps {
  game: Game;
}

export const GameCard: React.FC<GameCardProps> = ({ game }) => {
  return (
    <div className="text-2xl border-[1px] border-hint rounded-lg px-4 py-2 flex flex-col gap-4">
      <div className="flex gap-4 items-center justify-between">
        <h2>Default game</h2>
        <p className="text-primary flex gap-2 font-mono">
          <UsersIcon />
          {game.players.length}/{game.max_players}
        </p>
      </div>
      <div className="flex gap-4">
        <div
          className="grid gap-2"
          style={{
            gridTemplateColumns: `repeat(${game.max_players}, minmax(0, 1fr))`,
          }}
        >
          {game.players.map((player, i) => (
            <Avatar key={i} player={player} />
          ))}
          {Array.from({ length: game.max_players - game.players.length }).map(
            (_, i) => (
              <Avatar key={i} empty />
            )
          )}
        </div>
        <div className="flex gap-2 items-center justify-end">
          <JoinGameButton gameUUID="" />
        </div>
      </div>
    </div>
  );
};
