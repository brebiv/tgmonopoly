import { useGameStore } from "@/entities/gameStore";
import { GameBoard } from "./GameBoard";
import { PlayersSection } from "./PlayersSection";
import { useBoardConfig } from "@/shared/hooks/useBoardConfig";
import { ActionSheet } from "./ActionSheet";
import { DiceController } from "./DiceController";

export const Game = () => {
  const { game, players, isMyTurn } = useGameStore();
  // const { eventQueue } = useGameStore();
  // @ts-ignore
  const { data: boardConfig, isLoading: boardConfigLoading } = useBoardConfig(game.board_config, true, true);

  if (boardConfigLoading || !boardConfig) {
    return <h1>Loading board config</h1>;
  }

  return (
    <div className="bg-secondary-background flex h-screen flex-col gap-2">
      <GameBoard players={players} boardConfig={boardConfig}>
        <DiceController />
        {/* <div className="absolute flex flex-col">
          <p>Event queue length: {eventQueue.length}</p>
          <p>Events:</p>
          {eventQueue.map((event, i) => (
            <p key={i}>{event.event_type}</p>
          ))}
        </div> */}
      </GameBoard>
      <PlayersSection players={players} />
      <ActionSheet isOpen={isMyTurn} />
    </div>
  );
};
