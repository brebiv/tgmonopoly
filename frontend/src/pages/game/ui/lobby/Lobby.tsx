import { useGameStore } from "@/entities/gameStore";
import { LeaveGameButton } from "@/features/leave-game/LeaveGameButton";
import { Card } from "@/shared/ui/Card";
import { PlayerCard } from "@/shared/ui/PlayerCard";

export const Lobby = () => {
  const pathname = location.pathname;
  const gameUUID = pathname.split("/").filter(Boolean).pop() ?? null;

  /////// ADD AUTH HERE, move auth logic from HomePage to context provider so that it will become reusable

  const players = useGameStore((s) => s.players);
  const game = useGameStore((s) => s.game);

  if (!gameUUID) {
    console.error("Could not get UUID from url");
    return;
  }

  return (
    <div className="bg-secondary-background relative flex h-screen w-full flex-col items-center gap-4 px-8 pt-2">
      <h1>Game lobby</h1>
      <Card className="w-full">
        <h2>Players</h2>
        <div className="flex w-full flex-col gap-2">
          {players && players.map((player, i) => <PlayerCard key={i} player={player} />)}
          {game &&
            players &&
            Array.from({ length: game.max_players - players.length }).map((_, i) => <PlayerCard key={i} />)}
        </div>
      </Card>
      <div className="w-full">
        <LeaveGameButton gameUUID={gameUUID} />
      </div>
    </div>
  );
};
