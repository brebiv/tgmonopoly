import { useEffect } from "react";
import Board from "./Board";

function Game() {
  useEffect(() => {
    // @ts-ignore
    // window.Telegram.WebApp.BackButton.hide();
    window.Telegram.WebApp.BackButton.show();
    // @ts-ignore
    window.Telegram.WebApp.BackButton.onClick(() => {
      window.location.href = "/";
      // @ts-ignore
      window.Telegram.WebApp.BackButton.hide();
      return true;
    });
  }, []);

  return (
    <div
      className="flex min-h-screen flex-col"
      style={{
        backgroundColor:
          // @ts-ignore
          window.Telegram.WebApp.themeParams.bg_color || "#334155",
      }}
    >
      <Board />
    </div>
  );
}

export default Game;
