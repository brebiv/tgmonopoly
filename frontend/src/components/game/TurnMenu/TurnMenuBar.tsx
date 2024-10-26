import { useGameStore } from "@/stores/GameStore";
import { useTheme } from "@/stores/ThemeContext";
import { Minus } from "lucide-react";

function TurnMenuBar() {
  const setShowTurnMenu = useGameStore((state) => state.setShowTurnMenu);

  const { bgColor, textColor } = useTheme();

  return (
    <div
      className="absolute bottom-0 flex h-[6%] w-full items-center justify-center rounded-t-lg"
      onMouseDown={() => setShowTurnMenu(true)}
      style={{
        backgroundColor: bgColor,
        color: textColor,
      }}
    >
      <Minus size={42} />
    </div>
  );
}

export default TurnMenuBar;
