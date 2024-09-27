import { Player, PlayerChip as PlayerChipType } from "@/types/api";
import PlayerChip from "./PlayerChip";
import { useEffect, useRef, useState } from "react";

function PlayersChipController({
  players,
  boardLoaded,
}: {
  players: Player[] | [] | any;
  boardLoaded: boolean;
}) {
  if (players == undefined || players.length == 0) {
    return null;
  }

  const [playerChips, setPlayerChips] = useState<PlayerChipType[]>([]);
  const tilePositions = useRef({});

  // Collect tile positions
  useEffect(() => {
    if (!boardLoaded) {
      return;
    }

    const tiles = document.querySelectorAll(".tile[data-position]");
    tiles.forEach((tile) => {
      const position = tile.getAttribute("data-position");
      const rect = tile.getBoundingClientRect();
      // @ts-ignore
      tilePositions.current[position] = {
        x: rect.x,
        y: rect.y,
        width: rect.width,
        height: rect.height,
      };
    });
  }, [boardLoaded]);

  useEffect(() => {
    if (!boardLoaded) {
      return;
    }

    console.log({ players });

    console.log("players", players);

    const groupedByPosition = players.reduce((acc: any, player: Player) => {
      if (!acc[player.position]) {
        acc[player.position] = [];
      }
      acc[player.position].push(player);
      return acc;
    }, {});

    console.log("groupedByPosition", groupedByPosition);

    const newPlayerChips = [];
    const tilePositionsWithPlayers = Object.keys(groupedByPosition).map((key) => parseInt(key));

    for (let i = 0; i < tilePositionsWithPlayers.length; i++) {
      let position = tilePositionsWithPlayers[i];
      // @ts-ignore
      let tilePos = tilePositions.current[position];
      // let position = Object.keys(groupedByPosition)
      for (let j = 0; j < groupedByPosition[position].length; j++) {
        let player = groupedByPosition[position][j];
        let playersOnTheTile = groupedByPosition[position];
        let halfChipSize = 6;
        let x, y;
        let side = position < 10 ? 0 : position < 20 ? 1 : position < 30 ? 2 : 3;
        if (i == 0 || i == 10 || i == 20 || i == 30) {
          side = -1;
        }

        if (playersOnTheTile.length == 1) {
          x = tilePos.x + tilePos.width / 2 - halfChipSize;
          y = tilePos.y + tilePos.height / 2 - halfChipSize;
        } else if (playersOnTheTile.length == 2) {
          if (side == 0 || side == 2) {
            if (j == 0) {
              x = tilePos.x + tilePos.width / 2 - halfChipSize;
              y = tilePos.y + tilePos.height / 4 - halfChipSize;
            } else if (j == 1) {
              x = tilePos.x + tilePos.width / 2 - halfChipSize;
              y = tilePos.y + tilePos.height / 2 + halfChipSize;
            }
          } else if (side == 1 || side == 3 || side == -1) {
            if (j == 0) {
              x = tilePos.x + tilePos.width / 4 - halfChipSize;
              y = tilePos.y + tilePos.height / 2 - halfChipSize;
            } else if (j == 1) {
              x = tilePos.x + tilePos.width / 1.4 - halfChipSize;
              y = tilePos.y + tilePos.height / 2 - halfChipSize;
            }
          }
        } else if (playersOnTheTile.length == 3) {
          let offset = 2;
          if (side == 0 || side == 2) {
            if (j == 0) {
              x = tilePos.x + tilePos.width / 2 - halfChipSize;
              y = tilePos.y + tilePos.height / 4 + offset - halfChipSize;
            } else if (j == 1) {
              x = tilePos.x + tilePos.width / 3.8 - halfChipSize;
              y = tilePos.y + tilePos.height / 1.8 + offset - halfChipSize;
            } else if (j == 2) {
              x = tilePos.x + tilePos.width / 1.3 - halfChipSize;
              y = tilePos.y + tilePos.height / 1.8 + offset - halfChipSize;
            }
          } else if (side == 1 || side == 3 || side == -1) {
            if (j == 0) {
              x = tilePos.x + tilePos.width / 3.5 - halfChipSize;
              y = tilePos.y + tilePos.height / (2 - 0.5) - halfChipSize;
            } else if (j == 1) {
              x = tilePos.x + tilePos.width / 1.4 - halfChipSize;
              y = tilePos.y + tilePos.height / (2 - 0.5) - halfChipSize;
            } else if (j == 2) {
              x = tilePos.x + tilePos.width / 2 - halfChipSize;
              y = tilePos.y + tilePos.height / (2 + 1.7) - halfChipSize;
            }
          }
        } else if (playersOnTheTile.length == 4) {
          if (side == 0 || side == 1 || side == 2 || side == 3 || side == -1) {
            if (j == 0) {
              x = tilePos.x + tilePos.width / 3.8 - halfChipSize;
              y = tilePos.y + tilePos.height / (2 - 0.5) - halfChipSize;
            } else if (j == 1) {
              x = tilePos.x + tilePos.width / 1.25 - halfChipSize;
              y = tilePos.y + tilePos.height / (2 - 0.5) - halfChipSize;
            } else if (j == 2) {
              x = tilePos.x + tilePos.width / 3.8 - halfChipSize;
              y = tilePos.y + tilePos.height / (2 + 1.7) - halfChipSize;
            } else if (j == 3) {
              x = tilePos.x + tilePos.width / 1.25 - halfChipSize;
              y = tilePos.y + tilePos.height / (2 + 1.7) - halfChipSize;
            }
          }
        }

        newPlayerChips.push({
          ...player,
          x: x,
          y: y,
          side: side,
        });
      }
    }
    console.log("here");
    console.log({ newPlayerChips });
    setPlayerChips(newPlayerChips);
  }, [players, boardLoaded]);

  useEffect(() => {
    console.log({ playerChips });
  }, [playerChips]);

  return (
    <div className="players absolute">
      {playerChips.map((playerChip) => (
        <PlayerChip
          key={playerChip.id}
          left={playerChip.x}
          top={playerChip.y}
          color={playerChip.color}
        />
      ))}
    </div>
  );
}

export default PlayersChipController;
