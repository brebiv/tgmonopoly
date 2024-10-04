import { sendGameAction } from "@/api";
import { Button } from "@/components/ui/button";
import { GameActionType } from "@/types/api";
import { Dices } from "lucide-react";

function RollDiceButton({ gameUUID }: { gameUUID: string }) {
  return (
    <Button
      style={{
        backgroundColor:
          // @ts-ignore
          window.Telegram.WebApp.themeParams.button_color || "black",
        color:
          // @ts-ignore
          window.Telegram.WebApp.themeParams.button_text_color || "white",
      }}
      onClick={() => {
        sendGameAction({ action: GameActionType.ROLL_DICE, game_uuid: gameUUID });
      }}
      className="w-full gap-2 py-6 text-lg font-semibold"
    >
      <Dices />
      Roll dice
    </Button>
  );
}

export default RollDiceButton;
