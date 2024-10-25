import { sendGameAction } from "@/api";
import { Button } from "@/components/ui/button";
import { GameActionType } from "@/types/api";
import { Dices } from "lucide-react";

function RollDiceButton({ gameUUID, disabled }: { gameUUID: string; disabled?: boolean }) {
  return (
    <Button
      variant={"default"}
      onClick={() => {
        sendGameAction({ action: GameActionType.ROLL_DICE, game_uuid: gameUUID });
      }}
      disabled={disabled}
      className="w-full gap-2 py-6 text-lg font-semibold"
    >
      <Dices />
      Roll dice
    </Button>
  );
}

export default RollDiceButton;
