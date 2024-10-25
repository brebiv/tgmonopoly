import { Sheet } from "react-modal-sheet";
import { useGameStore } from "@/stores/GameStore";
import TurnMenuBar from "./TurnMenuBar";
import MenuContent from "./MenuContent";
import { useTheme } from "@/stores/ThemeContext";

function TurnMenu() {
  const showTurnMenu = useGameStore((state) => state.showTurnMenu);
  const setShowTurnMenu = useGameStore((state) => state.setShowTurnMenu);

  const { me } = useGameStore((state) => state);
  //   const ref = useRef<SheetRef>();
  //   const snapTo = (i: number) => ref.current?.snapTo(i);

  const { textColor, bgColor } = useTheme();

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
            backgroundColor: bgColor,
            color: textColor,
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
