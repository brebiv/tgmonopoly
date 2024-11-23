import { Sheet } from "react-modal-sheet";
import { useGameStore } from "@/stores/GameStore";
import TurnMenuBar from "./TurnMenuBar";
import MenuContent from "./MenuContent";
import { useTheme } from "@/stores/ThemeContext";
import { useTelegramInitParams } from "@/hooks";
import { ChevronDown } from "lucide-react";

function TurnMenu() {
  const showTurnMenu = useGameStore((state) => state.showTurnMenu);
  const setShowTurnMenu = useGameStore((state) => state.setShowTurnMenu);

  const { me } = useGameStore((state) => state);
  //   const ref = useRef<SheetRef>();
  //   const snapTo = (i: number) => ref.current?.snapTo(i);

  const { textColor, bgColor } = useTheme();
  const initParams = useTelegramInitParams();

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
          {/* Header */}
          <Sheet.Header>
            {(initParams?.tgWebAppPlatform === "tdesktop" ||
              initParams?.tgWebAppPlatform === "web") && (
              <div
                className="my-2 flex h-10 items-center justify-center gap-2 px-4"
                onClick={() => {
                  setShowTurnMenu(false);
                }}
              >
                <ChevronDown viewBox="4 4 16 16" className="h-full" />
              </div>
            )}
          </Sheet.Header>
          <Sheet.Content>
            <MenuContent effects={me?.effects || []} />
          </Sheet.Content>
        </Sheet.Container>
      </Sheet>
    </div>
  );
}

export default TurnMenu;
