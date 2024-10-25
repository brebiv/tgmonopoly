import { sendGameAction } from "@/api";
import { Button } from "@/components/ui/button";
import { GameActionType } from "@/types/api";
import { DollarSign } from "lucide-react";

function BuyPropertyButton({ gameUUID }: { gameUUID: string }) {
  return (
    <Button
      variant={"default"}
      onClick={() => {
        sendGameAction({ action: GameActionType.BUY_PROPERRTY, game_uuid: gameUUID });
      }}
      className="w-full gap-2 py-6 text-lg font-semibold"
    >
      <DollarSign />
      Buy
    </Button>
  );
}

export default BuyPropertyButton;
