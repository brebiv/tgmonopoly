import type { Player } from "@/entities/types";
import { PlayerChip } from "./PlayChip";
import type React from "react";
import { useEffect, useRef, useState } from "react";

const PLAYER_CHIP_SIZE_PX = 12;
const CORNER_TILE_PADDING = 0.25 / 2;

interface PlayerChipControllerProps {
  players: Player[];
}

export const PlayerChipController: React.FC<PlayerChipControllerProps> = ({ players }) => {
  const playersAreaRef = useRef<HTMLDivElement | null>(null);
  const [ready, setReady] = useState(false);

  const calculatePlayerChipPosition = (
    player: Player,
    players: Player[],
  ):
    | {
        x: number;
        y: number;
      }
    | undefined => {
    let tile: HTMLElement | null = document.querySelector(`.tile[data-position="${player.position}"]`);
    if (!tile) {
      console.warn("Was not able to find tile for player chip. Position:", player.position);
      return;
    }
    if (!playersAreaRef.current) {
      console.warn("Was not able to get playerArea ref");
      return;
    }

    let playerAreaBoundingBox = playersAreaRef.current.getBoundingClientRect();
    let tileBoundingBox = tile.getBoundingClientRect();

    let playersOnTheTile = players.filter((p) => p.position == player.position);
    let playersOnTheTileCount = playersOnTheTile.length;

    let possiblePositions = [];

    let centerX = tileBoundingBox.x + tileBoundingBox.width * 0.5 - PLAYER_CHIP_SIZE_PX / 2;
    let centerY = tileBoundingBox.y + tileBoundingBox.height * 0.5 - PLAYER_CHIP_SIZE_PX / 2;

    switch (playersOnTheTileCount) {
      case 1:
        possiblePositions.push({ x: centerX, y: centerY });
        break;
      case 2:
        possiblePositions.push({
          x: tileBoundingBox.x + tileBoundingBox.width * CORNER_TILE_PADDING,
          y: tileBoundingBox.y + tileBoundingBox.height * CORNER_TILE_PADDING,
        });
        possiblePositions.push({
          x: tileBoundingBox.right - tileBoundingBox.width * CORNER_TILE_PADDING - PLAYER_CHIP_SIZE_PX,
          y: tileBoundingBox.bottom - PLAYER_CHIP_SIZE_PX - tileBoundingBox.height * CORNER_TILE_PADDING,
        });
        break;
      case 3:
        possiblePositions.push({
          x: tileBoundingBox.x + tileBoundingBox.width * 0.5 - PLAYER_CHIP_SIZE_PX / 2,
          y: tileBoundingBox.y + tileBoundingBox.height * CORNER_TILE_PADDING,
        });
        possiblePositions.push({
          x: tileBoundingBox.left + tileBoundingBox.width * CORNER_TILE_PADDING,
          y: tileBoundingBox.bottom - PLAYER_CHIP_SIZE_PX - tileBoundingBox.height * CORNER_TILE_PADDING,
        });
        possiblePositions.push({
          x: tileBoundingBox.right - tileBoundingBox.width * CORNER_TILE_PADDING - PLAYER_CHIP_SIZE_PX,
          y: tileBoundingBox.bottom - PLAYER_CHIP_SIZE_PX - tileBoundingBox.height * CORNER_TILE_PADDING,
        });
        break;
      case 4:
        possiblePositions.push({
          x: tileBoundingBox.x + tileBoundingBox.width * CORNER_TILE_PADDING,
          y: tileBoundingBox.y + tileBoundingBox.height * CORNER_TILE_PADDING,
        });
        possiblePositions.push({
          x: tileBoundingBox.right - tileBoundingBox.width * CORNER_TILE_PADDING - PLAYER_CHIP_SIZE_PX,
          y: tileBoundingBox.y + tileBoundingBox.height * CORNER_TILE_PADDING,
        });
        possiblePositions.push({
          x: tileBoundingBox.left + tileBoundingBox.width * CORNER_TILE_PADDING,
          y: tileBoundingBox.bottom - PLAYER_CHIP_SIZE_PX - tileBoundingBox.height * CORNER_TILE_PADDING,
        });
        possiblePositions.push({
          x: tileBoundingBox.right - tileBoundingBox.width * CORNER_TILE_PADDING - PLAYER_CHIP_SIZE_PX,
          y: tileBoundingBox.bottom - PLAYER_CHIP_SIZE_PX - tileBoundingBox.height * CORNER_TILE_PADDING,
        });
        break;
      default:
        console.warn(
          `Could not calculate possible positions for ${playersOnTheTileCount} users and tile pos ${player.position}`,
        );
    }

    possiblePositions = possiblePositions.map((pos) => ({
      x: pos.x - playerAreaBoundingBox.x,
      y: pos.y - playerAreaBoundingBox.y,
    }));

    if (possiblePositions.length == 0) {
      console.warn("Could not calculate possible positions for tile", player.position);
    }

    let tilePlayerIndex = playersOnTheTile.findIndex((p) => p.id == player.id);
    return possiblePositions[tilePlayerIndex];
  };

  useEffect(() => {
    setReady(true);
  }, []);

  return (
    <div ref={playersAreaRef} id="players" className="absolute h-full w-full">
      {ready &&
        players.map((player) => {
          let position = calculatePlayerChipPosition(player, players);
          if (!position) {
            return;
          }

          return <PlayerChip player={player} size={PLAYER_CHIP_SIZE_PX} x={position.x} y={position.y} />;
        })}
    </div>
  );
};
