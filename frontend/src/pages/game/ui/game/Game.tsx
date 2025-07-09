import { useGameStore } from "@/entities/gameStore";
import { GameBoard } from "./GameBoard";
import { PlayersSection } from "./PlayersSection";
import { useBoardConfig } from "@/shared/hooks/useBoardConfig";

export const Game = () => {
  const { game, players } = useGameStore();
  if (!game) {
    return <h1>Loading game</h1>;
  }
  const { data: boardConfig, isLoading: boardConfigLoading } = useBoardConfig(game.board_config, true, true);

  if (boardConfigLoading || !boardConfig) {
    return <h1>Loading board config</h1>;
  }

  return (
    <div className="bg-secondary-background flex h-screen flex-col gap-2">
      <GameBoard players={players} boardConfig={boardConfig} />
      <PlayersSection players={players} />
    </div>
  );
};
