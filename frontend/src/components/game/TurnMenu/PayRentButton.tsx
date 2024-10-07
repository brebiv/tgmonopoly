import { sendGameAction } from "@/api";
import { Button } from "@/components/ui/button";
import { GameActionType } from "@/types/api";
import { Banknote } from "lucide-react";

function PayRentButton({ gameUUID }: { gameUUID: string }) {
  return (
    <Button
      style={{
        backgroundColor:
          // @ts-ignore
          window.Telegram.WebApp.themeParams.destructive_text_color || "black",
        color:
          // @ts-ignore
          window.Telegram.WebApp.themeParams.button_text_color || "white",
      }}
      onClick={() => {
        sendGameAction({ action: GameActionType.PAY_RENT, game_uuid: gameUUID });
      }}
      className="w-full gap-2 py-6 text-lg font-semibold"
    >
      <Banknote />
      Pay
    </Button>
  );
}

export default PayRentButton;
