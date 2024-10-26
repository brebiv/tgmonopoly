import { sendGameAction } from "@/api";
import { Button } from "@/components/ui/button";
import { PRISON_PAY_AMOUNT } from "@/config";
import { GameActionType } from "@/types/api";
import { HandCoins } from "lucide-react";

function PrisonPayButton({ gameUUID, disabled }: { gameUUID: string; disabled?: boolean }) {
  return (
    <Button
      variant={"default"}
      onClick={() => {
        sendGameAction({ action: GameActionType.PAY_FOR_PRISON, game_uuid: gameUUID });
      }}
      className="w-full gap-2 py-6 text-lg font-semibold"
      disabled={disabled}
    >
      <HandCoins />
      <p>
        Pay <span className="font-thin">${PRISON_PAY_AMOUNT}</span>
      </p>
    </Button>
  );
}

export default PrisonPayButton;
