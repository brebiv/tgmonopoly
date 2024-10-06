import { Sheet } from "react-modal-sheet";
import { useGameStore } from "@/stores/GameStore";
import TurnMenuBar from "./TurnMenuBar";
import MenuContent from "./MenuContent";

function TurnMenu() {
  const showTurnMenu = useGameStore((state) => state.showTurnMenu);
  const setShowTurnMenu = useGameStore((state) => state.setShowTurnMenu);

  const { me } = useGameStore((state) => state);
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
            <MenuContent effects={me?.effects || []} />
          </Sheet.Content>
        </Sheet.Container>
      </Sheet>
    </div>
  );
}

export default TurnMenu;
