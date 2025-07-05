import { useGameStore } from "@/entities/gameStore";
import { useBoardConfig } from "@/shared/hooks/useBoardConfig";
import { TileRenderer } from "./TileRenderer";

export const GameBoard = () => {
  const { game } = useGameStore();
  const { data: boardConfig, isLoading: boardConfigLoading } = useBoardConfig(
    game.board_config,
    true,
    true,
  );

  if (boardConfigLoading || !boardConfig) {
    return <h1>Loading</h1>;
  }

  return (
    <div className="aspect-square w-full bg-amber-200">
      <TileRenderer tiles={boardConfig?.tiles} />
    </div>
  );
};
