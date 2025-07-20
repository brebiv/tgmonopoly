import { createPortal } from "react-dom";
import { useGameStore } from "@/entities/gameStore";
import { GameBoard } from "./GameBoard";
import { PlayersSection } from "./PlayersSection";
import { ActionSheet } from "./ActionSheet";
import { ConfettiController } from "./ConfettiController";
import { GameBoardOverlay } from "./GameBoardOverlay";

export const Game = () => {
  const tilesLoaded = useGameStore((s) => s.tilesLoaded);

  return (
    <div className="bg-secondary-background flex h-screen flex-col gap-3">
      <ConfettiController />
      <GameBoard />
      {tilesLoaded && createPortal(<GameBoardOverlay />, document.getElementById("board-center")!)}
      <PlayersSection />
      <ActionSheet />
    </div>
  );
};
