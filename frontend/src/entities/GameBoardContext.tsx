import React, { createContext, useContext } from "react";
import type { BoardConfig } from "./types";

interface GameBoardContextData {
  boardConfig: BoardConfig;
}
const GameBoardContext = createContext<GameBoardContextData | undefined>(undefined);

interface GameBoardContextProps {
  boardConfig: BoardConfig;
  children: React.ReactNode;
}

export const GameBoardContextProvider: React.FC<GameBoardContextProps> = ({ boardConfig, children }) => {
  const value = { boardConfig: boardConfig };
  return <GameBoardContext.Provider value={value}>{children}</GameBoardContext.Provider>;
};

export const useGameBoardContext = (): GameBoardContextData => {
  const context = useContext(GameBoardContext);
  if (!context) {
    throw new Error("useGameBoardContext must be used within a GameBoardContextProvider");
  }
  return context;
};
