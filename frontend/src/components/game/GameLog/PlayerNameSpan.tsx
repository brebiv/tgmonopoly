import { getPlayerById } from "@/lib/utils";
import { Player } from "@/types/api";

function PlayerNameSpan({ player }: { player: Player | number }) {
  let playerToBeRendered = player as Player;

  if (typeof player === "number") {
    let _player = getPlayerById(player);
    if (_player) {
      playerToBeRendered = _player;
    } else {
      return <span style={{ color: "black" }}>Unknown</span>;
    }
  }

  return <span style={{ color: playerToBeRendered.color }}>{playerToBeRendered.name}</span>;
}

export default PlayerNameSpan;
