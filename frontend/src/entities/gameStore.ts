import { create } from "zustand";
import { devtools } from "zustand/middleware";

import { type BoardConfig, type Game, type GameEvent, type GameFrame, type Player, type Tile } from "./types";
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
  dices?: number[];
  showDices: boolean;
  showActionSheet: boolean;
  processEventGameFrame: (gameFrame: GameFrame) => void;
  processInitialGameFrame: (gameFramge: GameFrame) => void;
  enqueueEvents: (events: GameEvent[]) => void;
  processEventQueue: () => Promise<void>;

  // Utils
  getTileByPosition: (position: number) => Tile | undefined;
};

export const useGameStore = create<GameState>(
  // @ts-ignore
  devtools((set, get) => ({
    isProcessingEvents: false,
    eventQueue: [],
    eventLog: [],
    players: [],
    game: undefined,
    boardConfig: undefined,
    isMyTurn: false,
    showDices: false,
    showActionSheet: false,
    processInitialGameFrame: (gameFrame) => {
      let myPlayer = gameFrame.players.find((p) => p.id == gameFrame.my_player_id);
      if (!myPlayer) {
        throw new Error("Could not find my player");
      }
      let isMyTurn = myPlayer.id === gameFrame.game.current_player;

      set({
        players: gameFrame.players,
        game: gameFrame.game,
        myPlayer: myPlayer,
        isMyTurn: isMyTurn,
        boardConfig: gameFrame.board_config,
        showActionSheet: isMyTurn,
        // ownerships: gameFrame.game.ownerships,
      });
    },
    processEventGameFrame: async (gameFrame) => {
      // Pre events procssing logic
      console.log("Processing event game frame", gameFrame);
      get().enqueueEvents(gameFrame.events);
      set({ showActionSheet: false });
      await get().processEventQueue();

      // Post event processing logic
      console.log("Done processing event game frame", gameFrame);
      let isMyTurn = gameFrame.game.current_player === get().myPlayer?.id;
      let myPlayer = gameFrame.players.find((p) => p.id == get().myPlayer?.id);
      if (!myPlayer) {
        throw new Error("Could not find my player");
      }
      // Make sure that all state is updated after event processing did partial updates
      set({
        isMyTurn: isMyTurn,
        myPlayer: myPlayer,
        players: gameFrame.players,
        game: gameFrame.game,
        showActionSheet: isMyTurn,
      });
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

    // Utils
    getTileByPosition: (position) => {
      const { boardConfig } = get();
      return boardConfig?.tiles.find((tile) => tile.position === position);
    },
  })),
);
