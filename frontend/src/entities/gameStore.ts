import { create } from "zustand";
import { devtools } from "zustand/middleware";
import type { BoardConfig, Game, GameEvent, GameFrame, Player } from "./types";

type GameState = {
  eventQueue: GameEvent[];
  eventLog: GameEvent[];
  isProcessingGameEvent: boolean;
  players: Player[];
  game: Game;
  board_config: BoardConfig;
  processGameFrame: (gameFrame: GameFrame) => void;
  addEvents: (events: GameEvent[]) => void;
  processNextEvent: () => void;
};

export const useGameStore = create<GameState>()(
  devtools((set, get) => ({
    eventQueue: [],
    eventLog: [],
    isProcessingGameEvent: false,
    processGameFrame: (gameFrame) => {
      console.log("Processing game frame", gameFrame);
      get().addEvents(gameFrame.events);
      set({ players: gameFrame.players, game: gameFrame.game });
    },
    addEvents: (events) => {
      set((state) => ({
        eventQueue: [...state.eventQueue, ...events],
      }));
    },
    processNextEvent: () => {},
  }))
);
