import { create } from "zustand";
import { type BoardConfig, type Game, type GameEvent, type GameFrame, type Player } from "./types";
import { processEvent } from "@/app/lib/gameEventProcessing/processEvent";

export type GameState = {
  isProcessingEvents: boolean;
  eventQueue: GameEvent[];
  eventLog: GameEvent[];
  players: Player[];
  game?: Game;
  boardConfig?: BoardConfig;
  myPlayer?: Player;
  isMyTurn: boolean;
  processEventGameFrame: (gameFrame: GameFrame) => void;
  processInitialGameFrame: (gameFramge: GameFrame) => void;
  enqueueEvents: (events: GameEvent[]) => void;
  processEventQueue: () => void;
};

export const useGameStore = create<GameState>()((set, get) => ({
  isProcessingEvents: false,
  eventQueue: [],
  eventLog: [],
  players: [],
  game: undefined,
  boardConfig: undefined,
  isMyTurn: false,
  processInitialGameFrame: (gameFrame) => {
    set({
      players: gameFrame.players,
      game: gameFrame.game,
      myPlayer: gameFrame.players.find((p) => p.id == gameFrame.my_player_id),
      isMyTurn:
        gameFrame.players.find((p) => p.id == gameFrame.my_player_id)?.id === gameFrame.game.current_player,
    });
  },
  processEventGameFrame: async (gameFrame) => {
    console.log("Processing event game frame", gameFrame);
    get().enqueueEvents(gameFrame.events);
    get().processEventQueue();
  },

  enqueueEvents: (events) => {
    set((state) => ({
      eventQueue: [...state.eventQueue, ...events],
    }));
  },

  processEventQueue: async () => {
    if (get().isProcessingEvents) return;

    set({ isProcessingEvents: true });
    while (get().eventQueue.length) {
      const event = get().eventQueue[0];
      await processEvent(event, set, get);
      set((state) => ({
        eventQueue: state.eventQueue.slice(1),
      }));
    }
    set({ isProcessingEvents: false });
  },
}));
