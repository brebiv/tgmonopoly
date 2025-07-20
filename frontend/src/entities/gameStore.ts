import { shallow } from "zustand/shallow";
import { create } from "zustand";
import { devtools } from "zustand/middleware";

import {
  GameStatus,
  PendingActionTypes,
  type BoardConfig,
  type Game,
  type GameEvent,
  type GameFrame,
  type Ownership,
  type Player,
  type Tile,
} from "./types";
import { processEvent } from "@/app/lib/gameEventProcessing/processEvent";

export type GameState = {
  isProcessingEvents: boolean;
  eventQueue: GameEvent[];
  eventLog: GameEvent[];
  players: Player[];
  ownerships: Ownership[];
  game?: Game;
  gameStatus?: GameStatus;
  boardConfig?: BoardConfig;
  myPlayer?: Player;
  isMyTurn: boolean;
  dices?: number[];
  showDices: boolean;
  showActionSheet: boolean;
  casinoBet?: number;
  isCasinoBet?: boolean;
  flipCoin?: boolean;
  isWonCasino?: boolean;
  casinoPlayer?: Player;
  tilesLoaded: boolean;
  processEventGameFrame: (gameFrame: GameFrame) => void;
  processInitialGameFrame: (gameFramge: GameFrame) => void;
  enqueueEvents: (events: GameEvent[]) => void;
  processEventQueue: () => Promise<void>;
  setCasinoBet: (value: number) => void;
  setIsCasinoBet: (value: boolean) => void;
  setIsWonCasino: (value: boolean) => void;
  setTilesLoaded: (value: boolean) => void;

  // Utils
  getTileByPosition: (position: number) => Tile | undefined;
  getOwnershipByPosition: (position: number) => Ownership | undefined;
  getPlayerById: (id: number) => Player | undefined;
};

export const useGameStore = create<GameState>(
  // @ts-ignore
  devtools((set, get) => ({
    isProcessingEvents: false,
    eventQueue: [],
    eventLog: [],
    players: [],
    ownerships: [],
    game: undefined,
    boardConfig: undefined,
    isMyTurn: false,
    showDices: false,
    showActionSheet: false,
    casinoBet: undefined,
    tilesLoaded: false,
    processInitialGameFrame: (gameFrame) => {
      let myPlayer = gameFrame.players.find((p) => p.id == gameFrame.my_player_id);
      if (!myPlayer) {
        throw new Error("Could not find my player");
      }
      let isMyTurn = myPlayer.id === gameFrame.game.current_player;
      let casinoPlayer = gameFrame.players.find(
        (p) => p.pending_action?.action_type == PendingActionTypes.IN_CASINO,
      );

      set({
        players: gameFrame.players,
        game: gameFrame.game,
        gameStatus: gameFrame.game.status,
        myPlayer: myPlayer,
        isMyTurn: isMyTurn,
        boardConfig: gameFrame.board_config,
        showActionSheet: isMyTurn,
        casinoPlayer: casinoPlayer,
        ownerships: gameFrame.game.ownerships,
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
      const newState = {
        isMyTurn: isMyTurn,
        myPlayer: myPlayer,
        players: gameFrame.players,
        game: gameFrame.game,
        gameStatus: gameFrame.game.status,
        showActionSheet: isMyTurn,
        casinoBet: undefined,
        isCasinoBet: undefined,
        flipCoin: undefined,
        isWonCasino: undefined,
        casinoPlayer: undefined,
      };

      // If ownerships didn't change, don't trigger rerender
      if (!shallow(get().ownerships, gameFrame.game.ownerships)) {
        Object.assign(newState, {
          ownerships: gameFrame.game.ownerships,
        });
      }
      set(newState);
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
    setCasinoBet: (value) => {
      set({ casinoBet: value });
    },
    setIsCasinoBet: (value) => {
      set({ isCasinoBet: value });
    },
    setIsWonCasino: (value) => {
      set({ isWonCasino: value });
    },
    setTilesLoaded: (value) => {
      set({ tilesLoaded: value });
    },

    // Utils
    getTileByPosition: (position) => {
      const { boardConfig } = get();
      return boardConfig?.tiles.find((tile) => tile.position === position);
    },
    getOwnershipByPosition: (position) => {
      const { game } = get();
      return game?.ownerships.find((o) => o.tile_position === position);
    },
    getPlayerById: (id) => {
      const { game } = get();
      return game?.players.find((p) => p.id === id);
    },
  })),
);
