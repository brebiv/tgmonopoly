import { useGameStore } from "@/entities/gameStore";
import { GameBoard } from "./GameBoard";
import { PlayersSection } from "./PlayersSection";
import { ActionSheet } from "./ActionSheet";
import { DiceController } from "./DiceController";
import { useActionSheetConfig } from "@/shared/hooks/useActionSheetConfig";
import { Button } from "@/shared/ui/Button";

export const Game = () => {
  const { players, boardConfig, game, showActionSheet } = useGameStore();
  // const { eventQueue } = useGameStore();
  const actionSheetCfg = useActionSheetConfig(boardConfig, showActionSheet);

  if (!boardConfig) {
    return <h1>Loading board config</h1>;
  }

  return (
    <div className="bg-secondary-background flex h-screen flex-col gap-3">
      <GameBoard players={players} boardConfig={boardConfig}>
        <DiceController />
        {import.meta.env.DEV && (
          <div>
            <Button
              className="absolute top-0"
              onClick={() => {
                // @ts-ignore
                window.open(`http://localhost:8000/api/games/${game?.uuid}/`, "_blank").focus();
              }}
            >
              Go to api
            </Button>
            {/* <div className="absolute flex flex-col">
          <p>Event queue length: {eventQueue.length}</p>
          <p>Events:</p>
          {eventQueue.map((event, i) => (
            <p key={i}>{event.event_type}</p>
          ))}
        </div> */}
          </div>
        )}
      </GameBoard>
      <PlayersSection players={players} />
      {actionSheetCfg && <ActionSheet isOpen={showActionSheet} {...actionSheetCfg} />}
    </div>
  );
};
