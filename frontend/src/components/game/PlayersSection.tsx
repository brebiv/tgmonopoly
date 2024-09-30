import { Player } from "@/types/api";
import PlayerCard from "./PlayerCard";
import { usePlayers } from "@/hooks";

function PlayersSection() {
  const { data: players = [] } = usePlayers();
  // @ts-ignore
  if (players == undefined || players.length == 0) {
    return <h1 className="text-white">Loading</h1>;
  }
  return (
    <div className="grid grid-cols-2 gap-2 px-2">
      {
        // @ts-ignore
        players.map((player: Player) => (
          <PlayerCard key={player.id} player={player} />
        ))
      }
    </div>
  );
}

export default PlayersSection;
