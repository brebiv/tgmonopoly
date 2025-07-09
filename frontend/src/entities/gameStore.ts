import { create } from "zustand";
import type { BoardConfig, Game, GameEvent, GameFrame, Player } from "./types";

type GameState = {
  eventQueue: GameEvent[];
  eventLog: GameEvent[];
  isProcessingGameEvent: boolean;
  players: Player[];
  game?: Game;
  boardConfig?: BoardConfig;
  processGameFrame: (gameFrame: GameFrame) => void;
  addEvents: (events: GameEvent[]) => void;
  processNextEvent: () => void;
};

export const useGameStore = create<GameState>()((set, get) => ({
  eventQueue: [],
  eventLog: [],
  isProcessingGameEvent: false,
  // players: MOCK_PLAYERS.slice(0, 100),
  players: [],
  game: undefined,
  boardConfig: undefined,
  processGameFrame: (gameFrame) => {
    console.log("Processing game frame", gameFrame);
    get().addEvents(gameFrame.events);
    set({ players: gameFrame.players, game: gameFrame.game });
    // set({ game: gameFrame.game });
  },

  addEvents: (events) => {
    set((state) => ({
      eventQueue: [...state.eventQueue, ...events],
    }));
  },

  processNextEvent: () => {},
}));

// export const useGameStore = create<GameState>()(
//   devtools((set, get) => ({
//     eventQueue: [],
//     eventLog: [],
//     isProcessingGameEvent: false,
//     players: MOCK_PLAYERS.slice(0, 100),
//     processGameFrame: (gameFrame) => {
//       console.log("Processing game frame", gameFrame);
//       get().addEvents(gameFrame.events);
//       // set({ players: gameFrame.players, game: gameFrame.game });
//       set({ game: gameFrame.game });
//     },
//     addEvents: (events) => {
//       set((state) => ({
//         eventQueue: [...state.eventQueue, ...events],
//       }));
//     },
//     processNextEvent: () => {},
//   })),
// );
