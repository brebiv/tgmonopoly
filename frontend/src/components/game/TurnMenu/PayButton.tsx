import { sendGameAction } from "@/api";
import { Button } from "@/components/ui/button";
import { GameActionType, Player } from "@/types/api";
import { Banknote } from "lucide-react";

function PayButton({
  gameUUID,
  player,
  amount,
}: {
  gameUUID: string;
  player?: Player;
  amount?: number;
}) {
  let disabled = false;
  if (player && amount) {
    disabled = player.cash < amount;
  }

  return (
    <Button
      variant={"destructive"}
      onClick={() => {
        sendGameAction({ action: GameActionType.PAY, game_uuid: gameUUID });
      }}
      className="w-full gap-2 py-6 text-lg font-semibold"
      disabled={disabled}
    >
      <Banknote />
      Pay
    </Button>
  );
}

export default PayButton;
