import { sendGameAction } from "@/api";
import { Button } from "@/components/ui/button";
import { GameActionType } from "@/types/api";
import { Banknote } from "lucide-react";

function PayButton({ gameUUID }: { gameUUID: string }) {
  return (
    <Button
      variant={"destructive"}
      onClick={() => {
        sendGameAction({ action: GameActionType.PAY, game_uuid: gameUUID });
      }}
      className="w-full gap-2 py-6 text-lg font-semibold"
    >
      <Banknote />
      Pay
    </Button>
  );
}

export default PayButton;
