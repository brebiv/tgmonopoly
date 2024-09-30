import { useEffect, useState } from "react";
import { Sheet } from "react-modal-sheet";
import { useGameStore } from "@/stores/GameStore";
import { Minus } from "lucide-react";
import { Button } from "../ui/button";
import { sendGameAction } from "@/api";
import { GameActionType } from "@/types/api";

function TurnMenu() {
  const [isOpen, setIsOpen] = useState(false);
  const myTurn = useGameStore((state) => state.myTurn);
  const gameUUID = window.location.pathname.split("/")[2];

  useEffect(() => {
    console.log("myTurn", myTurn);

    // setIsOpen(myTurn);
  }, [myTurn]);

  return (
    <div>
      <div
        className="absolute bottom-0 flex h-[6%] w-full items-center justify-center rounded-t-lg"
        onMouseDown={() => setIsOpen(true)}
        style={{
          backgroundColor:
            // @ts-ignore
            window.Telegram.WebApp.themeParams.bg_color || "#334155",
          color:
            // @ts-ignore
            window.Telegram.WebApp.themeParams.text_color || "white",
        }}
      >
        <Minus size={42} />
      </div>
      <Sheet isOpen={isOpen} onClose={() => setIsOpen(false)} detent="content-height">
        <Sheet.Container
          style={{
            backgroundColor:
              // @ts-ignore
              window.Telegram.WebApp.themeParams.bg_color || "#334155",
            color:
              // @ts-ignore
              window.Telegram.WebApp.themeParams.text_color || "white",
          }}
        >
          <Sheet.Header />
          <Sheet.Content>
            <div className="flex flex-col items-center gap-2 pb-4">
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
              >
                Roll dice
              </Button>
            </div>
          </Sheet.Content>
        </Sheet.Container>
      </Sheet>
    </div>
  );
}

export default TurnMenu;
