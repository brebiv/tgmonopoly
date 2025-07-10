import { create } from "zustand";
import type { BoardConfig, Game, GameEvent, GameFrame, Player } from "./types";

type GameState = {
  eventQueue: GameEvent[];
  eventLog: GameEvent[];
  isProcessingGameEvent: boolean;
  players: Player[];
  game?: Game;
  boardConfig?: BoardConfig;
  myPlayer?: Player;
  isMyTurn: boolean;
  processGameFrame: (gameFrame: GameFrame) => void;
  addEvents: (events: GameEvent[]) => void;
  processNextEvent: () => void;
};

export const useGameStore = create<GameState>()((set, get) => ({
  eventQueue: [],
  eventLog: [],
  isProcessingGameEvent: false,
  players: [],
  game: undefined,
  boardConfig: undefined,
  isMyTurn: false,
  processGameFrame: (gameFrame) => {
    console.log("Processing game frame", gameFrame);
    let state = get();
    let myPlayer = gameFrame.players.find((player) => player.id == gameFrame.my_player_id);
    let isMyTurn = gameFrame.game.current_player === myPlayer!.id;

    state.addEvents(gameFrame.events);
    set({ players: gameFrame.players, game: gameFrame.game, isMyTurn: isMyTurn, myPlayer: myPlayer });
  },

  addEvents: (events) => {
    set((state) => ({
      eventQueue: [...state.eventQueue, ...events],
    }));
  },

  processNextEvent: () => {},
}));
