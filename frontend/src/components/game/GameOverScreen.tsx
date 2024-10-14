import { useGameStore } from "@/stores/GameStore";
import { useEffect } from "react";

function GameOverScreen() {
  const { setShowTurnMenu } = useGameStore.getState();
  useEffect(() => {
    setShowTurnMenu(false);
  }, []);

  return (
    <div
      className="absolute z-40 flex h-full w-full flex-col items-center justify-center"
      style={{
        // @ts-ignore
        color: window.Telegram.WebApp.themeParams.text_color || "white",
      }}
    >
      <h1 className="z-10">Game Over</h1>
      <div
        className="absolute h-full w-full opacity-90"
        style={{
          // @ts-ignore
          backgroundColor: window.Telegram.WebApp.themeParams.bg_color || "#334155",
          // @ts-ignore
          color: window.Telegram.WebApp.themeParams.text_color || "white",
        }}
      ></div>
    </div>
  );
}

export default GameOverScreen;
