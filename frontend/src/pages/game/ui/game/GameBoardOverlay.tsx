import { PendingActionTypes } from "@/entities/types";
import { Button } from "@/shared/ui/Button";
import { CasinoMenu } from "./CasinoMenu";
import { DiceController } from "./DiceController";
import { useGameStore } from "@/entities/gameStore";

const DebugOverlay = () => {
  return (
    <div>
      <Button
        className="absolute top-0"
        onClick={() => {
          // @ts-ignore
          window.open(`http://localhost:8000/api/games/${gameUUID}/`, "_blank").focus();
        }}
      >
        Go to api
      </Button>
    </div>
  );
};

export const GameBoardOverlay = () => {
  const myPlayer = useGameStore((s) => s.myPlayer);

  if (!myPlayer) {
    return <h1>Loading myPlayer</h1>;
  }

  return (
    <>
      <DiceController />
      {myPlayer.pending_action?.action_type == PendingActionTypes.IN_CASINO && (
        <CasinoMenu player={myPlayer} />
      )}
      {import.meta.env.DEV && <DebugOverlay />}
    </>
  );
};
