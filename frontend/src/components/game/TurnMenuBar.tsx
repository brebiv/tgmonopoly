import { useGameStore } from "@/stores/GameStore";
import { Minus } from "lucide-react";

function TurnMenuBar() {
  const setShowTurnMenu = useGameStore((state) => state.setShowTurnMenu);

  return (
    <div
      className="absolute bottom-0 flex h-[6%] w-full items-center justify-center rounded-t-lg"
      onMouseDown={() => setShowTurnMenu(true)}
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
  );
}

export default TurnMenuBar;
