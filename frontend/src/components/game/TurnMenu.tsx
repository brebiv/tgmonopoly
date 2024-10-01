import { Sheet } from "react-modal-sheet";
import { useGameStore } from "@/stores/GameStore";
import { Dices } from "lucide-react";
import { Button } from "../ui/button";
import { sendGameAction } from "@/api";
import { GameActionType } from "@/types/api";
import TurnMenuBar from "./TurnMenuBar";

function TurnMenu() {
  const showTurnMenu = useGameStore((state) => state.showTurnMenu);
  const setShowTurnMenu = useGameStore((state) => state.setShowTurnMenu);
  const gameUUID = window.location.pathname.split("/")[2];
  //   const ref = useRef<SheetRef>();
  //   const snapTo = (i: number) => ref.current?.snapTo(i);

  return (
    <div>
      <TurnMenuBar />
      <Sheet
        isOpen={showTurnMenu}
        onClose={() => setShowTurnMenu(false)}
        snapPoints={[0.6]}
        detent="content-height"
      >
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
            <div className="flex flex-col items-center gap-4 px-2 pb-12">
              <h1 className="text-2xl font-semibold">It's your turn!</h1>
              <div className="flex w-full flex-col">
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
              </div>
            </div>
          </Sheet.Content>
        </Sheet.Container>
      </Sheet>
    </div>
  );
}

export default TurnMenu;
